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

"""Scenario of Congestion Warning."""

# import pandas as pd
# from post_process_algo import post_process
# from pre_process_ai_algo.algo_lib import utils as process_tools
# from typing import Dict
# from typing import List


class Base:
    """Super class of congestion warning class."""

    def run(
        self,
        context_frames: dict,
        current_frame: dict,
        last_timestamp: int,
        intersection_id: str,
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class CongestionWarning(Base):
    """Scenario of Congestion Warning."""

    def run(
        self,
        context_frames: dict,
        current_frame: dict,
        last_timestamp: int,
        intersection_id: str,
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

        last_timestamp:
        Timestamp of current frame data for the next call

        """
        self._intersection_id = intersection_id
        self._show_info: List[dict] = []
        self._congestion_warning_message: List[dict] = []
        self._current_frame = current_frame
        df = pd.DataFrame(self._current_frame).T
        if "lane" in df.columns and "lane" in df.columns:
            df["speed"] = df["speed"].apply(lambda x: abs(int(x/3.6)))
            df.groupby("lane").apply(self.cal)  # type: ignore
        return (
            self._congestion_warning_message,
            self._show_info,
            last_timestamp,
        )

    def cal(self, df_lane):
        """Cal."""
        lane_info: Dict = {}
        if "lane" not in df_lane.columns:
            return
        df_id = df_lane.drop_duplicates(subset=["lane"], keep="first")
        lane_id = df_id.to_dict('records')[0]["lane"]
        lane_info["lane_id"] = lane_id
        if self._get_direction(lane_id) > 0:
            return
        else:
            congestion_level = 0
            avg_speed = df_lane["speed"].mean()
            if 25 <= avg_speed < 30:
                congestion_level = 1
            elif 15 <= avg_speed < 25:
                congestion_level = 2
            elif 0 <= avg_speed < 15:
                congestion_level = 3
            df_lane.sort_values("refPos_lat", inplace=True)
            start_point = df_lane.head(
                1)[["refPos_lat", "refPos_lon", "x", "y"]].to_dict('records')[0]
            end_point = df_lane.tail(
                1)[["refPos_lat", "refPos_lon", "x", "y"]].to_dict('records')[0]

            lane_info["congestion_level"] = congestion_level
            lane_info["start_point"] = start_point
            lane_info["end_point"] = end_point

            info_for_show, info_for_cgw = self._build_cgw_event(
                lane_info, lane_id)
            self._show_info.append(info_for_show)
            self._congestion_warning_message.append(info_for_cgw)

    def _get_direction(self, lane):
        return post_process.lane_info[self._intersection_id][lane]

    def _build_cgw_event(self, lane_info: dict, id: str) -> tuple:
        info_for_show, info_for_cgw = self._message_generate(lane_info, id)
        return info_for_show, info_for_cgw

    def _message_generate(self, lane_info: dict, lane_id: str) -> tuple:
        info_for_show = {
            "type": "CGW",
            "level": lane_info["congestion_level"],
            "start_point": {
                "x": lane_info['start_point']["x"],
                "y": lane_info['start_point']["y"],
            },
            "end_point": {
                "x": lane_info['end_point']["x"],
                "y": lane_info['end_point']["y"],
            }
        }
        info_for_cgw = {
            "laneInfo": {
                "laneId": lane_id,
                "startPos": {
                    "lat": int(lane_info["start_point"]["refPos_lat"]),
                    "lon": int(lane_info["start_point"]["refPos_lon"]),
                },
                "endPos": {
                    "lat": int(lane_info["end_point"]["refPos_lat"]),
                    "lon": int(lane_info["end_point"]["refPos_lon"]),
                }
            }
        }
        return info_for_show, info_for_cgw
