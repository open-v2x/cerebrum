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

"""Scenario of OverSpeed Warning."""
import aiohttp
from common import modules
import grpc.aio  # type: ignore
import json
from post_process_algo import post_process
from scenario_algo.external import over_speed_grpc_pb2
from scenario_algo.external import over_speed_grpc_pb2_grpc
from websockets.client import connect


class Base:
    """Super class of overspeed warning class."""

    async def run(
        self,
        context_frames: dict,
        current_frame: dict,
        last_timestamp: int,
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class OverspeedWarning(Base):
    """Scenario of OverSpeed Warning."""

    def __init__(self) -> None:  # noqa
        self.endpoint_config = (
            modules.algorithms.overspeed_warning.endpoint_config
        )
        self.connect = None
        self.service_type = self.endpoint_config.get("service_type").split(
            "/"
        )[-1]

    async def _connect_websocket(self):
        self.connect = await connect(self.endpoint_config.get("endpoint_url"))

    async def _connect_http(self):
        self.connect = aiohttp.ClientSession()

    async def _connect_grpc(self):
        self.connect = grpc.aio.insecure_channel(
            self.endpoint_config.get("endpoint_url")
        )

    async def run(
        self,
        context_frames: dict,
        current_frame: dict,
        last_timestamp: int,
    ) -> tuple:  # noqa
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
        overspeed_warning_message:
        Overspeed warning message for broadcast, osw format

        last_timestamp:
        Timestamp of current frame data for the next call

        """

        if not self.connect:
            await getattr(self, f"_connect_{self.service_type}")()
        data = dict(
            context_frames=context_frames,
            current_frame=current_frame,
            last_timestamp=last_timestamp,
            speed_limits=post_process.speed_limits,
        )
        try:
            osw, show_info = await getattr(
                self, f"_run_from_external_{self.service_type}"
            )(data)
        except Exception:
            self.connect = None
        return osw, show_info, last_timestamp

    async def _run_from_external_websocket(self, data):
        await self.connect.send(json.dumps(data))
        res = await self.connect.recv()
        res = json.loads(res)
        return res.get("osw"), res.get("info")

    async def _run_from_external_http(self, data):
        async with self.connect.post(
            url=self.endpoint_config.get("endpoint_url"), json=data
        ) as response:
            res = await response.json()
            return res.get("osw"), res.get("info")

    async def _run_from_external_grpc(self, data):
        stub = over_speed_grpc_pb2_grpc.OverSpeedGrpcStub(self.connect)
        response = await stub.over_speed(
            over_speed_grpc_pb2.OverSpeedRequest(data=json.dumps(data))
        )
        res = json.loads(response.data)
        return res.get("osw"), res.get("show_info")
