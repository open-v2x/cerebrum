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

"""Scenario of DoNotPass Warning."""
from typing import Any
from typing import Dict

import aiohttp
from common import modules
import grpc.aio  # type: ignore
import json
from post_process_algo import post_process
from scenario_algo.do_not_pass_external import do_not_pass_grpc_pb2
from scenario_algo.do_not_pass_external import do_not_pass_grpc_pb2_grpc
from websockets.client import connect


class DoNotPass:
    """Scenario of DoNotPass Warning."""

    def __init__(self) -> None:  # noqa
        self.endpoint_config = (
            modules.algorithms.do_not_pass_warning.endpoint_config
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

    async def run(self, rsu_id, context_frame, latest_frame, msg_vir) -> tuple:
        """External call function.

        Input:
        context_frames : dict
        It is dict of history track data.

        latest_frame : dict
        It is the latest data obtain from RSU.

        msg_VIR : dict
        It is vehicle's lane-changing requirements from OBU

        transform_info:
        Information required for the conversion of latitude and longitude to
        the geodetic coordinate system

        rsu_id:
        RSU ID for getting the map info

        Output:
        msg_rsc : dict

        show_info: dict
        information for visualization

        """
        if not self.connect:
            await getattr(self, f"_connect_{self.service_type}")()

        data = dict(
            context_frame=context_frame,
            latest_frame=latest_frame,
            msg_vir=msg_vir,
            lane_info=post_process.lane_info,
        )
        try:
            msg, show_info = await getattr(
                self, f"_run_from_external_{self.service_type}"
            )(data)
        except Exception:
            self.connect = None
            return [], []
        return msg, show_info

    async def _run_from_external_websocket(self, data):
        await self.connect.send(json.dumps(data))
        res = await self.connect.recv()
        res = json.loads(res)
        return res.get("msg"), res.get("info")

    async def _run_from_external_http(self, data):
        async with self.connect.post(
            url=self.endpoint_config.get("endpoint_url"), json=data
        ) as response:
            res = await response.json()
            return res.get("msg"), res.get("info")

    async def _run_from_external_grpc(self, data):
        stub = do_not_pass_grpc_pb2_grpc.DoNotPassGrpcStub(self.connect)
        response = await stub.do_not_pass(
            do_not_pass_grpc_pb2.DoNotPassRequest(data=json.dumps(data))
        )
        res = json.loads(response.data)
        return res.get("msg"), res.get("info")
