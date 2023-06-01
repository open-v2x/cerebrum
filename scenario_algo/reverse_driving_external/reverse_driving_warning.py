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

"""Scenario of ReverseDriving Warning."""
import aiohttp  # noqa
from common import modules  # noqa
import grpc.aio  # type: ignore
import json  # noqa
from post_process_algo import post_process
from scenario_algo.reverse_driving_external import (  # noqa
    reverse_driving_grpc_pb2,  # noqa
)  # noqa
from scenario_algo.reverse_driving_external import (  # noqa
    reverse_driving_grpc_pb2_grpc,  # noqa
)  # noqa
from websockets.client import connect  # noqa


class Base:
    """Super class of reverse driving warning class."""

    def run(
        self,
        context_frames: dict,
        current_frame: dict,
        last_timestamp: int,
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class ReverseDriving(Base):
    """Scenario of ReverseDriving Warning."""

    def __init__(self) -> None:  # noqa
        self.endpoint_config = (
            modules.algorithms.reverse_driving_warning.endpoint_config
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

    async def run(  # type: ignore
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
        RevreseDriving_warning_message:
        RevreseDriving warning message for broadcast, osw format

        """
        if not self.connect:
            await getattr(self, f"_connect_{self.service_type}")()

        data = dict(
            context_frames=context_frames,
            current_frame=current_frame,
            last_timestamp=last_timestamp,
            lane_info=post_process.lane_info
        )

        try:
            rdw, show_info = await getattr(
                self, f"_run_from_external_{self.service_type}"
            )(data)
        except Exception as error:
            print(error)
            self.connect = None
            return [], [], last_timestamp
        return rdw, show_info, last_timestamp

    async def _run_from_external_websocket(self, data):
        await self.connect.send(json.dumps(data))
        res = await self.connect.recv()
        res = json.loads(res)
        return res.get("rdw"), res.get("info")

    async def _run_from_external_http(self, data):
        async with self.connect.post(
            url=self.endpoint_config.get("endpoint_url"), json=data
        ) as response:
            res = await response.json()
            return json.loads(res).get("rdw"), json.loads(res).get("info")

    async def _run_from_external_grpc(self, data):
        stub = reverse_driving_grpc_pb2_grpc.ReverseDrivingGrpcStub(
            self.connect
        )
        response = await stub.reverse_driving(
            reverse_driving_grpc_pb2.ReverseDrivingRequest(
                data=json.dumps(data)
            )
        )
        res = json.loads(response.data)
        return res.get("rdw"), res.get("info")
