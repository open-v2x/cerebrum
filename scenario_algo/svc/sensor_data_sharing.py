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

"""Call the sensor data sharing algorithm function."""

from common import consts
from common import modules
import orjson as json
from post_process_algo import post_process
from scenario_algo.svc.collision_warning import CollisionWarning

sensor_data_sharing = modules.algorithms.sensor_data_sharing.module


class SensorDataSharing:
    """Call the sensor data sharing algorithm function."""

    def __init__(self, kv, mqtt, mqtt_conn=None, node_id=None) -> None:
        """Class initialization."""
        self._kv = kv
        self._mqtt = mqtt
        self._mqtt_conn = mqtt_conn
        self.node_id = node_id
        self._exe = sensor_data_sharing.SensorDataSharing()

    async def run(
        self, params: dict, rsu_id: str, convert_info: list, node_id: int
    ) -> None:
        """External call function."""
        # 获取traj
        ptc_traj = await self._kv.get(
            CollisionWarning.TRAJS_KEY.format(rsu_id)
        )
        motor_traj = ptc_traj["motors"] if "motors" in ptc_traj else {}
        vptc_traj = ptc_traj["vptc"] if "vptc" in ptc_traj else {}

        # 获取 rsi
        rsi_formatter = modules.algorithms.rsi_formatter.module
        rsi = await self._kv.get(rsi_formatter.RSI.RSI_KEY.format(rsu_id))

        # 获取 rsu 经纬度
        sensor_pos = post_process.rsu_info[rsu_id]["pos"].copy()
        sensor_pos["lon"] = int(sensor_pos["lon"] * consts.CoordinateUnit)
        sensor_pos["lat"] = int(sensor_pos["lat"] * consts.CoordinateUnit)
        msg_ssm, info_for_show = self._exe.run(
            motor_traj, vptc_traj, rsi, params, sensor_pos, convert_info
        )
        if info_for_show:
            for i in info_for_show["other_cars"]:
                post_process.convert_for_visual(i, rsu_id)
            post_process.convert_for_visual(info_for_show["ego_point"], rsu_id)

        self._mqtt.publish(
            consts.SDS_TOPIC.format(rsu_id), json.dumps(msg_ssm), 0
        )
        self._mqtt.publish(
            consts.SDS_VISUAL_TOPIC.format(node_id),
            json.dumps([info_for_show]),
            0,
        )
