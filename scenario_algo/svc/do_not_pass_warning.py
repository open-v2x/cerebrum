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

"""Call the do not pass algorithm function."""

from common import consts
from common import modules
import orjson as json
from post_process_algo import post_process
from pre_process_ai_algo.algo_lib.utils import HIS_INFO_KEY
from scenario_algo import do_not_pass_external

do_not_pass_warning = modules.algorithms.do_not_pass_warning.module
if modules.algorithms.do_not_pass_warning.external_bool:
    do_not_pass_warning = getattr(do_not_pass_external, "do_not_pass")


class DoNotPass:
    """Call the do not pass algorithm function."""

    def __init__(self, kv, mqtt, mqtt_conn=None, node_id=None) -> None:
        """Class initialization."""
        self._kv = kv
        self._mqtt = mqtt
        self._mqtt_conn = mqtt_conn
        self.node_id = node_id
        self._exe = do_not_pass_warning.DoNotPass()

    async def run(
        self, params: dict, rsu_id: str, _: list, node_id: int
    ) -> None:  # noqa
        """External call function."""

        his_info = await self._kv.get(HIS_INFO_KEY.format(rsu_id))
        context_frames = (
            his_info["context_frames"]
            if his_info.get("context_frames")
            else {}
        )
        current_frame = (
            his_info["latest_frame"] if his_info.get("latest_frame") else {}
        )

        msg_rsc, info_for_show = await self._exe.run(
            rsu_id, context_frames, current_frame, params
        )
        if info_for_show:
            post_process.convert_for_visual(info_for_show["ego_point"], rsu_id)
            self._mqtt.publish(
                consts.DNP_VISUAL_TOPIC.format(node_id),
                json.dumps([info_for_show]),
                0,
            )
        if msg_rsc:
            self._mqtt.publish(
                consts.DNP_TOPIC.format(rsu_id), json.dumps(msg_rsc), 0
            )
