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

"""Send processed data to RSU and central platform."""

from common import consts
from common import modules
from config import devel as cfg
import orjson as json
from post_process_algo import post_process
from scenario_algo.svc import Base
from typing import Any
from typing import Dict


class Visualize(Base):
    """Send processed data to rsu and central platform."""

    def __init__(self, kv, mqtt, mqtt_conn=None, node_id=None):
        """Class initialization."""
        super().__init__(kv)
        self._mqtt = mqtt
        self._mqtt_conn = mqtt_conn
        self.node_id = node_id

    async def run(
        self,
        rsu: str,
        intersection_id: str,
        latest_frame: dict,
        node_id: int,
        _: dict = {},
    ) -> dict:
        """External call function."""
        # 可视化，修改 x，y 后，返回给 mqtt
        vis = []
        info_dict: Dict[str, Any] = {
            "moving_motor": 0,
            "motor": 0,
            "non-motor": 0,
            "pedestrian": 0,
            "motor_speed": 0,
        }
        for fr in latest_frame.values():
            frame = fr.copy()
            post_process.convert_for_visual(frame, intersection_id)
            info_dict[frame["ptcType"]] += 1
            if frame["ptcType"] == "motor" and frame["speed"] > 70:
                info_dict["moving_motor"] += 1
                info_dict["motor_speed"] += frame["speed"] * 0.02 * 3.6
            vis.append(frame)
        info_dict["motor_speed"] = (
            info_dict["motor_speed"] / info_dict["moving_motor"]
            if info_dict["moving_motor"]
            else 0
        )
        # get rsi
        rsi_formatter = modules.algorithms.rsi_formatter.module
        congestion = await self._kv.get(
            rsi_formatter.RSI.CONGESTION_KEY.format(intersection_id)
        )
        if congestion:
            congestion_info = "congestion"
        else:
            congestion_info = "free flow"
        final_info = {
            "rsuEsn": rsu,
            "vehicleTotal": info_dict["motor"],
            "averageSpeed": info_dict["motor_speed"],
            "pedestrianTotal": info_dict["pedestrian"],
            "congestion": congestion_info,
        }
        if cfg.cloud_server:
            url = cfg.cloud_server + "/homes/route_info_push"
            await post_process.http_post(url, final_info)
        if self._mqtt_conn:
            self._mqtt_conn.publish(
                consts.RSM_VISUAL_TOPIC.format(intersection_id, node_id),
                json.dumps(vis),
                0,
            )
        return latest_frame
