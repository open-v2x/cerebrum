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

"""Call the reverse driving warning algorithm function."""

from common import consts
from common import modules
import orjson as json
from post_process_algo import post_process
from pre_process_ai_algo.algo_lib.utils import HIS_INFO_KEY
from scenario_algo import reverse_driving_external


reverse_driving_warning = modules.algorithms.reverse_driving_warning.module

if modules.algorithms.reverse_driving_warning.external_bool:
    reverse_driving_warning = getattr(
        reverse_driving_external, "reverse_driving_warning"
    )


class ReverseDrivingWarning:
    """Call the reverse driving warning algorithm function."""

    def __init__(self, kv, mqtt, mqtt_conn=None, node_id=None):
        """Class initialization."""
        self._kv = kv
        self._exe = reverse_driving_warning.ReverseDriving()
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
        his_info = await self._kv.get(HIS_INFO_KEY.format(rsu_id))
        context_frames = (
            his_info["context_frames"]
            if his_info.get("context_frames")
            else {}
        )
        last_ts = his_info["last_ts"] if his_info.get("last_ts") else 0
        rdw, show_info, last_ts = await self._exe.run(
            context_frames, latest_frame, last_ts
        )
        post_process.convert_for_reverse_visual(show_info, rsu_id)
        reverse_driving_warning_message = post_process.generate_rdw(
            rdw, rsu_id
        )
        if rdw and show_info:
            self._mqtt.publish(
                consts.RDW_VISUAL_TOPIC.format(node_id),
                json.dumps(show_info),
                0,
            )
            self._mqtt.publish(
                consts.RDW_TOPIC.format(rsu_id),
                json.dumps(reverse_driving_warning_message),
                0,
            )
        return latest_frame
