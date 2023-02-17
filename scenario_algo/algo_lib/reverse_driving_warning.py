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

"""Scenario of Reverse Driving Warning."""

import numpy as np
from post_process_algo import post_process
from pre_process_ai_algo.algo_lib import utils as process_tools
from typing import List


class Base:
    """Super class of reverse driving warning class."""

    def run(
        self,
        context_frames: dict,
        current_frame: dict,
        last_timestamp: int,
        rsu_id: str,
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class ReverseDriving(Base):
    """Scenario of Reverse Driving Warning."""

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
        reverse_driving_warning_message:
        Reverse driving warning message for broadcast, rdw format

        event_list:
        Reverse driving warning information for visualization

        last_timestamp:
        Timestamp of current frame data for the next call

        """
        self._rsu_id = rsu_id
        self._show_info: List[dict] = []
        self._reverse_driving_warning_message: List[dict] = []
        self._current_frame = current_frame
        id_set, last_timestamp = process_tools.frames_combination(
            context_frames, self._current_frame, last_timestamp
        )

        # 只检查机动车的逆行情况
        check_ptc = ["motor"]
        dis_from_o_list = []
        origin_coor = self._get_origin_coor(self._rsu_id)
        for id in id_set:
            if self._current_frame[id]["ptcType"] in check_ptc:
                # 获取当前交通参与者所在车道线
                lane = self._current_frame[id]["lane"]
                if self._get_direction(lane) > 0:
                    # 判断该交通参与者当前帧和历史帧 x,y 坐标距离中心原点坐标的变化情况
                    for ptc in context_frames[id]:
                        dis_from_o_list.append(
                            self._cal_distance_from_o(ptc, origin_coor)
                        )
                    if self._strictly_increasing(dis_from_o_list):
                        info_for_show, info_for_rdw = self._build_rdw_event(
                            ptc, id
                        )
                        self._reverse_driving_warning_message.append(
                            info_for_rdw
                        )
                        self._show_info.append(info_for_show)
                        dis_from_o_list.clear()
                    else:
                        dis_from_o_list.clear()
                else:
                    # 判断该交通参与者当前帧和历史帧 x,y 坐标距离中心原点坐标的变化情况
                    for ptc in context_frames[id]:
                        dis_from_o_list.append(
                            self._cal_distance_from_o(ptc, origin_coor)
                        )
                    if self._strictly_decreasing(dis_from_o_list):
                        info_for_show, info_for_rdw = self._build_rdw_event(
                            ptc, id
                        )
                        self._reverse_driving_warning_message.append(
                            info_for_rdw
                        )
                        self._show_info.append(info_for_show)
                        dis_from_o_list.clear()
                    else:
                        dis_from_o_list.clear()
        return (
            self._reverse_driving_warning_message,
            self._show_info,
            last_timestamp,
        )

    def _get_origin_coor(self, rsu_id):
        return {"x": 80, "y": 55}

    def _get_direction(self, lane):
        return post_process.lane_info[self._rsu_id][lane]

    def _strictly_increasing(self, L):
        # 起步不做逆向计算
        if len(L) < 2:
            return False
        return all(x < y for x, y in zip(L, L[1:]))

    def _strictly_decreasing(self, L):
        if len(L) < 2:
            return False
        return all(x > y for x, y in zip(L, L[1:]))

    def _cal_distance_from_o(self, ptc, o):
        dx = ptc["x"] - o["x"]
        dy = ptc["y"] - o["y"]
        return np.sqrt(dx**2 + dy**2)

    def _build_rdw_event(self, ego: dict, id: str) -> tuple:
        info_for_show, info_for_rdw = self._message_generate(ego, id)
        return info_for_show, info_for_rdw

    def _message_generate(self, ego_info: dict, ego_id: str) -> tuple:

        info_for_show = {
            "ego": ego_id,
            "ego_current_point": [ego_info["x"], ego_info["y"]],
        }
        info_for_rdw = {
            "secMark": ego_info["secMark"],
            "egoInfo": {
                "egoId": ego_id,
                "egoPos": {
                    "lat": int(ego_info["lat"]),
                    "lon": int(ego_info["lon"]),
                },
                "speed": ego_info["speed"],
                "heading": ego_info["heading"],
                "width": ego_info["width"],
                "length": ego_info["length"],
                "height": ego_info["height"]
            },
        }
        return info_for_show, info_for_rdw
