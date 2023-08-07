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

"""Scenario of Sensor data sharing."""
import aiohttp
from common import modules
import grpc.aio  # type: ignore
import json
from scenario_algo.sensor_data_sharing_external import (
    sensor_data_sharing_grpc_pb2,
)  # noqa
from scenario_algo.sensor_data_sharing_external import (
    sensor_data_sharing_grpc_pb2_grpc,
)  # noqa

from websockets.client import connect


class Base:
    """Super class of SensorDataSharing class."""

    async def run(
        self,
        motor_kinematics: dict,
        vptc_kinematics: dict,
        rsi: dict,
        msg_VIR: dict,
        sensor_pos: dict,
        transform_info: list,
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class SensorDataSharing(Base):
    """Scenario of cooperative lane change."""

    def __init__(self) -> None:  # noqa
        self.endpoint_config = (
            modules.algorithms.sensor_data_sharing.endpoint_config
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
        motor_kinematics: dict,
        vptc_kinematics: dict,
        rsi: dict,
        msg_VIR: dict,
        sensor_pos: dict,
        transform_info: list,
    ) -> tuple:
        """External call function.

        Input:
        motor_kinematics : dict
        motors' kinematics information

        vptc_kinematics : dict
        vulnerable participants' kinematics information

        msg_VIR : dict
        It is vehicle's lane-changing requirements from OBU

        transform_info:
        Information required for the conversion of latitude and longitude to
        the geodetic coordinate system

        sensor_pos:
        RSU postion required for generating msg_SSM

        Output:
        msg_SSM : dict

        info_for_show : dict
        information for visualization

        """
        if not self.connect:
            await getattr(self, f"_connect_{self.service_type}")()
        data = dict(
            motor_kinematics=motor_kinematics,
            vptc_kinematics=vptc_kinematics,
            rsi=rsi,
            msg_VIR=msg_VIR,
            sensor_pos=sensor_pos,
            transform_info=[transform_info[1], transform_info[2]],
        )
        try:
            msg, show_info = await getattr(
                self, f"_run_from_external_{self.service_type}"
            )(data)
        except Exception as e:
            print(e)
            self.connect = None
            return [], []
        return msg, show_info

    async def _run_from_external_websocket(self, data):
        await self.connect.send(json.dumps(data))
        res = await self.connect.recv()
        res = json.loads(res)
        return (
            res.get("msg"),
            res.get("info"),
        )

    async def _run_from_external_http(self, data):
        async with self.connect.post(
            url=self.endpoint_config.get("endpoint_url"), json=data
        ) as response:
            res = await response.json()
            return (
                res.get("msg"),
                res.get("info"),
            )

    async def _run_from_external_grpc(self, data):
        stub = sensor_data_sharing_grpc_pb2_grpc.SensorDataSharingGrpcStub(  # noqa
            self.connect
        )
        response = await stub.sensor_data_sharing(
            sensor_data_sharing_grpc_pb2.SensorDataSharingRequest(
                data=json.dumps(data)
            )
        )
        res = json.loads(response.data)
        return (
            res.get("msg"),
            res.get("info"),
        )
