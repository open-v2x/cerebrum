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

""" Congestion Warning Algorithm."""

import numpy as np
import pandas as pd
from pre_process_ai_algo.algo_lib import utils as process_tools
from scenario_algo.algo_lib import utils
from typing import List
from typing import Any
from typing import Dict


class Base:
    """Super class of congestion warning class."""

    def run(
        self, context_frames: dict, current_frame: dict, last_timestamp: int
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class CongestionWarning(Base):
    """congestion warning algorithm.
    """

    def run(
        self,
        context_frames: dict,
        current_frame: dict,
        last_timestamp: int,
        rsu_id: str,
    ) -> tuple:
        """External call function.

           Input:  
           context_frames:
           Algorithm's historical frame data, obtained from the result of the last
           call, AID format

           current_frame:
           latest frame data, AID format

           last_timestamp:
           The current frame data timestamp when the algorithm function was last
           called

           Output:
           congestion_warning_message:
           Congestion warning message for broadcast, cgw format

           show_info:
           Congestion warning information for visualization

           last_timestamp:
           Timestamp of current frame data for the next call
       """
        self._rsu_id = rsu_id
        self._show_info: List[dict] = []
        self._congestion_warning_message: List[dict] = []
        self._current_frame = current_frame

        id_set, last_timestamp = process_tools.frames_combination(
            context_frames, self._current_frame, last_timestamp
        )

        # 拥堵计算只限于机动车
        check_ptc = ["motor"]
        motor_ptc = {}
        for id, obj_info in self._current_frame.items():
            if self._current_frame[id]["ptcType"] in check_ptc:
                motor_ptc[id] = obj_info
        df0 = pd.DataFrame(motor_ptc).T
        df0.groupby("lane").apply(self._cal_ave_speed_lane)

        return (
            self._congestion_warning_message,
            self._show_info,
            last_timestamp
        )

    def _cal_ave_speed_lane(self, df1):
        df1.sort_values(by="refPos_lat", inplace=True, ascending=True)
        ave_speed = df1["speed"].mean()
        id = df1["lane"].unique()[0]
        lane_info = {}
        if ave_speed < 35:
            if 0 <= ave_speed < 15:
                lane_info["level"] = 3
            elif 15 <= ave_speed < 25:
                lane_info["level"] = 2
            elif 25 <= ave_speed < 35:
                lane_info["level"] = 1

            start_point = df1.iloc[0:1, :][['refPos_lat',
                                            'refPos_lon']].to_dict(orient='records')[0]

            start_coor = df1.iloc[0:1, :][['x',
                                           'y']].to_dict(orient='records')[0]
            lane_info["start_point"] = start_point
            lane_info["start_coor"] = start_coor

            end_point = df1.iloc[-1:][['refPos_lat',
                                       'refPos_lon']].to_dict(orient='records')[0]
            end_coor = df1.iloc[0:1, :][['x',
                                        'y']].to_dict(orient='records')[0]
            lane_info["end_point"] = end_point
            lane_info["end_coor"] = end_coor

            # 构建拥堵数据
            info_for_show, info_for_sgw = self._build_cgw_event(
                lane_info, id
            )
            self._congestion_warning_message.append(
                info_for_sgw
            )
            self._show_info.append(info_for_show)

    def _build_cgw_event(self, lane: dict, id: int) -> tuple:
        info_for_show, info_for_cgw = self._message_generate(lane, id)
        return info_for_show, info_for_cgw

    def _message_generate(self, lane_info: dict, lane_id: int) -> tuple:

        info_for_show = {
            "type": "CGW",
            "ego_current_point": [lane_info["start_coor"]["x"], lane_info["end_coor"]["y"]],
        }
        info_for_cgw = {
            "congestionInfo": {
                "laneId": lane_id,
                "Pos": {
                    "startPoint": int(lane_info["start_point"]),
                    "endPoint": int(lane_info["end_point"]),
                },
                "level": lane_info["level"],
            },
        }
        return info_for_show, info_for_cgw
