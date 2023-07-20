#   Copyright 99Cloud, Inc. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

"""Scenario of Collision Warning."""
from typing import Any
from typing import Dict

import aiohttp
from common import modules
import grpc.aio  # type: ignore
import json
from scenario_algo.collision_external import collision_grpc_pb2
from scenario_algo.collision_external import collision_grpc_pb2_grpc
from websockets.client import connect


class CollisionWarning:
    """Scenario of DoNotPass Warning."""

    def __init__(self) -> None:  # noqa
        self.endpoint_config = (
            modules.algorithms.collision_warning.endpoint_config
        )
        self.connect = None
        self.service_type = self.endpoint_config.get("service_type").split(
            "/"
        )[-1]
        self.context_frame, self.latest_frame, self.msg_vir, self.lane_info = (
            Dict[str, Any],
            Dict[str, Any],
            Dict[str, Any],
            Dict[str, Any],
        )

    async def _connect_websocket(self):
        self.connect = await connect(self.endpoint_config.get("endpoint_url"))

    async def _connect_http(self):
        self.connect = aiohttp.ClientSession()

    async def _connect_grpc(self):
        self.connect = grpc.aio.insecure_channel(
            self.endpoint_config.get("endpoint_url")
        )

    async def run(
        self, context_frames: dict, current_frame: dict, last_timestamp: int
    ) -> tuple:
        """External call function.

        Input:
        context_frames:
        Algorithm's historical frame data, obtained from the result of the last
        call, AID format

        current_frame:
        latest frame data, AID format

        last_timestamp:
        The current frame data timestamp when the algorithm function was last
        called

        Output:
        collision_warning_message:
        Collision warning message for broadcast, CWM format

        event_list:
        Collision warning information for visualization

        last_timestamp:
        Timestamp of current frame data for the next call

        ptc_info["motors_kinematics"]:
        The kinematic information of the vehicle
        can be used in other scenarios such as sensor data sharing

        vptc_kinematics:
        The kinematic information of the vulnerable participants
        can be used in other scenarios such as sensor data sharing

        """
        if not self.connect:
            await getattr(self, f"_connect_{self.service_type}")()

        data = dict(
            context_frames=context_frames,
            current_frame=current_frame,
            last_timestamp=last_timestamp,
        )
        try:
            (
                msg,
                show_info,
                last_timestamp,
                motors_trajs,
                vptc_trajs,
            ) = await getattr(self, f"_run_from_external_{self.service_type}")(
                data
            )
            for key, value in motors_trajs.items():
                value["traj_point"] = [tuple(v) for v in value["traj_point"]]
                value["traj_footprint"] = [
                    tuple(tuple(i) for i in v) for v in value["traj_footprint"]
                ]
            for key, value in vptc_trajs.items():
                value["traj_point"] = [tuple(v) for v in value["traj_point"]]

        except Exception:
            self.connect = None
            return [], [], 0, [], []
        return msg, show_info, last_timestamp, motors_trajs, vptc_trajs

    async def _run_from_external_websocket(self, data):
        await self.connect.send(json.dumps(data))
        res = await self.connect.recv()
        res = json.loads(res)
        return (
            res.get("msg"),
            res.get("info"),
            res.get("last_timestamp"),
            res.get("motors_trajs"),
            res.get("vptc_trajs"),
        )

    async def _run_from_external_http(self, data):
        async with self.connect.post(
            url=self.endpoint_config.get("endpoint_url"), json=data
        ) as response:
            res = await response.json()
            return (
                res.get("msg"),
                res.get("info"),
                res.get("last_timestamp"),
                res.get("motors_trajs"),
                res.get("vptc_trajs"),
            )

    async def _run_from_external_grpc(self, data):
        stub = collision_grpc_pb2_grpc.CollisionGrpcStub(self.connect)
        response = await stub.collision(
            collision_grpc_pb2.CollisionRequest(data=json.dumps(data))
        )
        res = json.loads(response.data)
        return (
            res.get("msg"),
            res.get("info"),
            res.get("last_timestamp"),
            res.get("motors_trajs"),
            res.get("vptc_trajs"),
        )
