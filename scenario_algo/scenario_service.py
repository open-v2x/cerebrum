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

"""Match different scene algorithms."""

import orjson as json
from post_process_algo import post_process
from scenario_algo.svc.cooperative_lane_change import CooperativeLaneChange
from scenario_algo.svc.do_not_pass_warning import DoNotPass
from scenario_algo.svc.sensor_data_sharing import SensorDataSharing


class Service:
    """Match different scene algorithms."""

    def __init__(self, mqtt, kv, mqtt_conn=None) -> None:
        """Class initialization."""
        self._kv = kv
        self._mqtt = mqtt
        self._mqtt_conn = mqtt_conn
        self._sds = SensorDataSharing(kv, mqtt, mqtt_conn)
        self._clc = CooperativeLaneChange(kv, mqtt, mqtt_conn)
        self._dnp = DoNotPass(kv, mqtt, mqtt_conn)
        self._dispatch = {
            "sensorSharing": self._handle_sds,
            "laneChange": self._handle_clc,
            "retrograde": self._handle_dnp,
        }

    def _is_time_valid(self, msg_vir: dict) -> bool:
        if msg_vir["intAndReq"]["reqs"]["status"] not in [1, 2]:
            return False
        # current_time = time.time() * 1000 % consts.MaxSecMark
        # while current_time < msg_vir['secMark']:
        #     current_time += consts.MaxSecMark
        # if current_time - msg_vir['secMark'] >
        # msg_vir['intAndReq']['reqs'][
        #     'lifeTime'] * 10:
        #     return False
        return True

    async def run(self, rsu_id: str, payload: bytes) -> None:
        """External call function."""
        msg_vir = json.loads(payload)
        try:
            svc = list(msg_vir["intAndReq"]["reqs"]["info"].keys())[0]
        except IndexError:
            return None
        if self._is_time_valid(msg_vir):
            convert_info = [post_process.TfMap[rsu_id]] + [
                post_process.XOrigin[rsu_id],
                post_process.YOrigin[rsu_id],
            ]
            if self._dispatch.get(svc):
                await self._dispatch[svc](msg_vir, rsu_id, convert_info)

    async def _handle_sds(
        self, msg_vir: dict, rsu_id: str, convert_info: list
    ):
        await self._sds.run(msg_vir, rsu_id, convert_info)

    async def _handle_clc(
        self, msg_vir: dict, rsu_id: str, convert_info: list
    ):
        await self._clc.run(msg_vir, rsu_id, convert_info)

    async def _handle_dnp(
        self, msg_vir: dict, rsu_id: str, convert_info: list
    ):
        await self._dnp.run(msg_vir, rsu_id, convert_info)
