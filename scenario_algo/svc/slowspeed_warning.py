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

"""Call the slowspeed warning algorithm function."""

from common import consts
from common import modules
import orjson as json
from post_process_algo import post_process
from scenario_algo.svc.collision_warning import CollisionWarning

slowspeed_warning = modules.algorithms.slowspeed_warning.module  # type: ignore


class SlowspeedWarning:
    """Call the slowspeed warning algorithm function."""

    def __init__(self, kv, mqtt, mqtt_conn=None, node_id=None):
        """Class initialization."""
        self._kv = kv
        self._exe = slowspeed_warning.SlowspeedWarning()
        self._mqtt = mqtt
        self._mqtt_conn = mqtt_conn
        self.node_id = node_id

    async def run(
        self,
        rsu_id: str,
        latest_frame: dict,
        node_id: int,
        _: dict = {},
    ) -> dict:
        """External call function."""
        his_info = await self._kv.get(
            CollisionWarning.HIS_INFO_KEY.format(rsu_id)
        )
        context_frames = (
            his_info["context_frames"]
            if his_info.get("context_frames")
            else {}
        )
        last_ts = his_info["last_ts"] if his_info.get("last_ts") else 0
        ssw, show_info, last_ts = self._exe.run(
            context_frames, latest_frame, last_ts
        )
        post_process.convert_for_reverse_visual(show_info, rsu_id)
        slowspeed_warning_message = post_process.generate_osw(ssw, rsu_id)
        if ssw and show_info:
            self._mqtt.publish(
                consts.SSW_VISUAL_TOPIC.format(node_id),
                json.dumps(show_info),
                0,
            )
            self._mqtt.publish(
                consts.SSW_TOPIC.format(rsu_id),
                json.dumps(slowspeed_warning_message),
                0,
            )
        return latest_frame
