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

"""Call the congestion warning algorithm function."""

import ast
from common import consts
from common import modules
import orjson as json
import os
from post_process_algo import post_process
from pre_process_ai_algo.algo_lib.utils import HIS_INFO_KEY

congestion_warning = modules.algorithms.congestion_warning.module


class CongestionWarning:
    """Call the congestion warning algorithm function."""

    def __init__(self, kv, mqtt, mqtt_conn=None, node_id=None):
        """Class initialization."""
        self._kv = kv
        self._exe = congestion_warning.CongestionWarning()
        self._mqtt = mqtt
        self._mqtt_conn = mqtt_conn
        self.node_id = node_id

        # 判断拥堵级别，拥堵级别范围通过环境变量设置
        self.min_con_range = self._eval(os.getenv("min_con_range", [25, 30]))
        self.mid_con_range = self._eval(os.getenv("mid_con_range", [15, 24]))
        self.max_con_range = self._eval(os.getenv("max_con_range", [0, 14]))
        self.ranges = [
            self.max_con_range,
            self.mid_con_range,
            self.min_con_range,
        ]

        self.rectangles = [
            [[rect[0], rect[0]], [rect[1], rect[1]]] for rect in self.ranges
        ]

        if self.is_overlap():
            raise ValueError("三个拥堵范围相交,不进行拥堵计算")
        else:
            print("三个拥堵范围不相交")

    def _eval(self, range):
        if isinstance(range, str):
            range = ast.literal_eval(range)
        return range

    def is_overlap(self):
        """Isoverlap."""
        # 检查每对矩形是否有重叠
        for i in range(len(self.rectangles)):
            for j in range(i + 1, len(self.rectangles)):
                rect1 = self.rectangles[i]
                rect2 = self.rectangles[j]

                # 检查矩形的边界是否有重叠
                if (
                    rect1[0][0] <= rect2[1][0]
                    and rect1[1][0] >= rect2[0][0]
                    and rect1[0][1] <= rect2[1][1]
                    and rect1[1][1] >= rect2[0][1]
                ):
                    return True

        return False

    async def run(self, rsu: str, latest_frame: dict, _: dict = {}) -> dict:
        """External call function."""
        his_info = await self._kv.get(HIS_INFO_KEY.format(rsu))
        context_frames = (
            his_info["context_frames"]
            if his_info.get("context_frames")
            else {}
        )
        last_ts = his_info["last_ts"] if his_info.get("last_ts") else 0
        cgw, show_info, last_ts, CG_KEY = self._exe.run(
            context_frames,
            latest_frame,
            last_ts,
            rsu,
            self.min_con_range,
            self.mid_con_range,
            self.max_con_range,
        )

        cg_list = [item for item in show_info if item.get("level") > 0]
        if cg_list:
            await self._kv.set(CG_KEY, "congestion")
        if cgw and show_info:
            post_process.convert_for_congestion_visual(show_info, rsu)
            congestion_warning_message = post_process.generate_osw(cgw, rsu)
            self._mqtt.publish(
                consts.CGW_VISUAL_TOPIC.format(self.node_id),
                json.dumps(show_info),
                0,
            )
            self._mqtt.publish(
                consts.CGW_TOPIC.format(rsu),
                json.dumps(congestion_warning_message),
                0,
            )
        return latest_frame
