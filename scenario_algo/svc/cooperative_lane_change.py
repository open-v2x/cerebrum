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

"""Call the cooperative lane change algorithm function."""

import orjson as json
from post_process_algo import post_process
from scenario_algo.algo_lib import cooperative_lane_change
from scenario_algo.svc.collision_warning import CollisionWarning
from transform_driver import consts


class CooperativeLaneChange:
    """Call the cooperative lane change algorithm function."""

    def __init__(self, kv, mqtt, mqtt_conn=None, node_id=None) -> None:
        """Class initialization."""
        self._kv = kv
        self._mqtt = mqtt
        self._mqtt_conn = mqtt_conn
        self.node_id = node_id
        self._exe = cooperative_lane_change.CooperativeLaneChange()

    async def run(self, params: dict, rsu_id: str, convert_info: list) -> None:
        """External call function."""
        his_info = await self._kv.get(
            CollisionWarning.HIS_INFO_KEY.format(rsu_id)
        )
        context_frames = (
            his_info["context_frames"]
            if his_info.get("context_frames")
            else {}
        )
        current_frame = (
            his_info["latest_frame"] if his_info.get("latest_frame") else {}
        )

        msg_rsc, info_for_show = self._exe.run(
            convert_info, context_frames, current_frame, params
        )
        self._mqtt.publish(
            consts.CLC_TOPIC.format(rsu_id),
            json.dumps(msg_rsc),
            0,
        )
        if msg_rsc["coordinates"]["driveSuggestion"]["suggestion"] > 0:
            for i in info_for_show["traj_list_for_show"]:
                post_process.convert_for_visual(i, rsu_id)
            # rsu，前端
            if self._mqtt_conn:
                self._mqtt_conn.publish(
                    consts.CLC_VISUAL_TOPIC.format(rsu_id, self.node_id),
                    json.dumps([info_for_show]),
                    0,
                )
