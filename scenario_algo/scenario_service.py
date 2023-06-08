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

from common import modules
import orjson as json
from post_process_algo import post_process
from scenario_algo.svc.cooperative_lane_change import CooperativeLaneChange
from scenario_algo.svc.do_not_pass_warning import DoNotPass
from scenario_algo.svc.sensor_data_sharing import SensorDataSharing


class Service:
    """Match different scene algorithms."""

    def __init__(self, mqtt, kv, mqtt_conn=None, node_id=None) -> None:
        """Class initialization."""
        self.SM_CFG_KEY = "scenario_lastsm_and_cfg"
        self._kv = kv
        self._mqtt = mqtt
        self._sds = SensorDataSharing(kv, mqtt, mqtt_conn, node_id)
        self._clc = CooperativeLaneChange(kv, mqtt, mqtt_conn, node_id)
        self._dnp = DoNotPass(kv, mqtt, mqtt_conn, node_id)
        self._map = {
            "sensorSharing": "sensor_data_sharing",
            "laneChange": "cooperative_lane_change",
            "retrograde": "do_not_pass_warning",
        }
        self._pipelines = [
            "sensor_data_sharing",
            "cooperative_lane_change",
            "do_not_pass_warning"
        ]
        self._sensor_data_sharing_dispatch = {
            "disable": False,
            "sensor_data_sharing": self._sds,
        }
        self._cooperative_lane_change_dispatch = {
            "disable": False,
            "cooperative_lane_change": self._clc,
        }
        self._do_not_pass_warning_dispatch = {
            "disable": False,
            "do_not_pass_warning": self._dnp,
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

    async def _get_algo_version(self, svc, current_sec_mark):
        sm_and_cfg = await self._kv.get(self.SM_CFG_KEY)
        # last_sec_mark = sm_and_cfg["sm"] if sm_and_cfg.get("sm") else 0
        pipe_cfg = (
            sm_and_cfg["cfg"]
            if sm_and_cfg.get("cfg")
            else {
                "sensor_data_sharing": (
                    modules.algorithms.sensor_data_sharing.algo
                    if modules.algorithms.sensor_data_sharing.enable
                    else "disable"
                ),
                "cooperative_lane_change": (
                    modules.algorithms.cooperative_lane_change.algo
                    if modules.algorithms.cooperative_lane_change.enable
                    else "disable"
                ),
                "do_not_pass_warning": (
                    modules.algorithms.do_not_pass_warning.algo
                    if modules.algorithms.do_not_pass_warning.enable
                    else "disable"
                )
            }
        )
        # if 0 <= last_sec_mark - current_sec_mark <= 50000:
        #     return None
        await self._kv.set(  # type: ignore
            self.SM_CFG_KEY,  # type: ignore
            {"sm": current_sec_mark, "cfg": pipe_cfg},
        )

        # 根据意向请求确定具体场景算法
        p = self._map.get(svc)
        p_adopt = getattr(self, "_{}_dispatch".format(p)).get(
            pipe_cfg[p]
        )

        return p_adopt

    async def run(self, rsu_id: str, payload: bytes, node_id: int) -> None:
        """External call function."""
        msg_vir = json.loads(payload)
        try:
            svc = list(msg_vir["intAndReq"]["reqs"]["info"].keys())[0]
        except IndexError:
            return None
        current_sec_mark = msg_vir.get("secMark")
        if self._is_time_valid(msg_vir):
            convert_info = [post_process.TfMap[rsu_id]] + [
                post_process.XOrigin[rsu_id],
                post_process.YOrigin[rsu_id],
            ]
            if self._map.get(svc):
                p = await self._get_algo_version(svc, current_sec_mark)
                if p:
                    await p.run(msg_vir, rsu_id, convert_info, node_id)
