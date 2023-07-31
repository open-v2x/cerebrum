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

import numpy as np
import pandas as pd

from congestion_service import utils
from typing import Dict
from typing import List


MinDataDuration = 1.5  # 至少有多少秒的数据才计算车辆的动力学信息


class Base:
    """Super class of congestion warning class."""

    def run(
        self,
        context_frames: dict,
        current_frame: dict,
        last_timestamp: int,
        rsu: str,
        min_con_range: list,
        mid_con_range: list,
        max_con_range: list,
        lane_info: dict,
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class CongestionWarning(Base):
    """Scenario of Congestion Warning."""

    CG_KEY = "cg.{}"

    def run(
        self,
        context_frames: dict,
        current_frame: dict,
        last_timestamp: int,
        rsu: str,
        min_con_range: list,
        mid_con_range: list,
        max_con_range: list,
        lane_info: dict,
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
        self.rsu = rsu
        self.min_con_range = min_con_range
        self.mid_con_range = mid_con_range
        self.max_con_range = max_con_range
        self._show_info: List[dict] = []
        self._congestion_warning_message: List[dict] = []
        self._current_frame = current_frame
        self._lane_info = lane_info

        id_set, last_timestamp = utils.frames_combination(
            context_frames, self._current_frame, last_timestamp
        )

        # 拥堵情况只计算机动车
        check_ptc = ["motors"]
        ptc_info: dict = {"motors": {}}
        # 分别计算机动车、非机动车、行人的运动学信息，用于计算拥堵情况
        motors, non_motors, pedestrians = self._filter_ptcs(
            context_frames, last_timestamp, id_set
        )
        for ptc_type in check_ptc:
            ptc_info[ptc_type + "_kinematics"] = getattr(
                self, "_prepare_{}_kinematics".format(ptc_type)
            )(locals()[ptc_type])

        df = pd.DataFrame(ptc_info["motors_kinematics"]).T
        if df.empty:
            return (
                self._congestion_warning_message,
                self._show_info,
                last_timestamp,
                CongestionWarning.CG_KEY.format(rsu),
            )
        # 获取车道方向
        df["direction"] = df["lane"].apply(self._get_direction)
        # 车道方向是 驶向信号灯方向的 不做拥堵计算，因为信号灯数据还未输入
        df = df[df["direction"].isin([-1])]
        df.groupby("lane").apply(self.cal)  # type: ignore

        return (
            self._congestion_warning_message,
            self._show_info,
            last_timestamp,
            CongestionWarning.CG_KEY.format(rsu),
        )

    def cal(self, df_lane):
        """Cal."""
        # 车辆总数
        vehicle_data = len(df_lane)
        # 车道详细信息
        lane_info: Dict = {}  # type: ignore
        lane_id = df_lane["lane"].values[0]
        lane_info["lane_id"] = lane_id
        level = 0
        df_lane.sort_values("x", inplace=True, ascending=True)
        df_lane.reset_index(inplace=True)
        # 计算车辆与车辆之间的距离
        df_lane["dis_x"] = df_lane["x"].diff()
        df_lane["dis_y"] = df_lane["y"].diff()
        df_lane["dis"] = df_lane.apply(
            lambda x: np.sqrt(x["dis_x"] ** 2 + x["dis_y"] ** 2), axis=1
        )
        # 相邻两车距离大于100米。如何分段
        df1 = df_lane[df_lane["dis"] >= 200].index
        if df1.empty:
            pass
        else:
            pass
        start_point = df_lane.head(1)[["lat", "lon", "x", "y"]].to_dict(
            "records"
        )[0]
        end_point = df_lane.tail(1)[["lat", "lon", "x", "y"]].to_dict(
            "records"
        )[0]
        lane_info["start_point"] = start_point
        lane_info["end_point"] = end_point

        # df_lane[df_lane["speed"]*3.6 <= 30]
        # m/s * 3.6 == km/h
        avg_speed = df_lane["speed"].mean() * 3.6

        if vehicle_data >= 10:
            if self.min_con_range[0] <= avg_speed <= self.min_con_range[1]:
                level = 1
            elif self.mid_con_range[0] <= avg_speed <= self.mid_con_range[1]:
                level = 2
            elif self.max_con_range[0] <= avg_speed <= self.max_con_range[1]:
                level = 3

        lane_info["level"] = level
        lane_info["avg_speed"] = avg_speed
        lane_info["secMark"] = df_lane["secMark"].values[0]

        info_for_show, info_for_cgw = self._build_cgw_event(lane_info, lane_id)
        self._show_info.append(info_for_show)
        self._congestion_warning_message.append(info_for_cgw)

    def _filter_ptcs(
        self, context_frames: dict, last_timestamp: int, id_set: set
    ) -> tuple:
        timestamp_threshold = last_timestamp - (MinDataDuration * 1000)
        motors = dict()
        non_motors = dict()
        pedestrians = dict()
        for guid, ptc_info in context_frames.items():
            filtered = [
                v
                for v in ptc_info
                if v["timeStamp"] >= timestamp_threshold
                and v["global_track_id"] in id_set
            ]
            if len(filtered) <= 4:
                continue
            if filtered[-1]["timeStamp"] == filtered[-2]["timeStamp"]:
                continue
            if ptc_info[-1]["ptcType"] == "motor":
                motors[guid] = filtered
            elif ptc_info[-1]["ptcType"] == "non-motor":
                non_motors[guid] = filtered
            elif ptc_info[-1]["ptcType"] == "pedestrian":
                pedestrians[guid] = filtered
        return motors, non_motors, pedestrians

    def _prepare_motors_kinematics(self, motors: dict) -> dict:
        # 返回各个车辆运动学信息的字典
        ret = {}
        for k, mot in motors.items():
            # 关键数据转换为列表存储，方便计算差值、均值等信息
            ret[k] = {
                "ptcId": k,
                "lane": mot[-1]["lane"],
                "secMark": mot[-1]["secMark"],
                "x": mot[-1]["x"],
                "y": mot[-1]["y"],
                "lat": mot[-1]["lat"],
                "lon": mot[-1]["lon"],
                "x_list": [v["x"] for v in mot],
                "y_list": [v["y"] for v in mot],
                "timeStamp": [(v["timeStamp"] / 1000) for v in mot],
                "guid": k,
            }
            # 车辆按顺序计算速度
            getattr(self, "_calc_speed")(ret[k])
        return ret

    def _calc_speed(self, kinematics: dict) -> None:
        x = kinematics["x_list"]
        y = kinematics["y_list"]
        timeStamp = kinematics["timeStamp"]

        # 运用差分公式计算历史轨迹的线速度
        xd = utils.differentiate(x, timeStamp)
        yd = utils.differentiate(y, timeStamp)

        # 基于历史轨迹的信息，计算均值作为估计的未来运动学信息
        kinematics["speed_x"] = utils.mean(xd)
        kinematics["speed_y"] = utils.mean(yd)
        kinematics["speed"] = np.linalg.norm(  # type: ignore
            [kinematics["speed_x"], kinematics["speed_y"]]
        ).tolist()

    def _get_direction(self, lane):
        return self._lane_info[str(lane)]

    def _build_cgw_event(self, lane_info: dict, id: str) -> tuple:
        info_for_show, info_for_cgw = self._message_generate(lane_info, id)
        return info_for_show, info_for_cgw

    def _message_generate(self, lane_info: dict, lane_id: str) -> tuple:
        info_for_show = {
            "type": "CGW",
            "level": lane_info["level"],
            "startPoint": {
                "x": lane_info["start_point"]["x"],
                "y": lane_info["start_point"]["y"],
            },
            "endPoint": {
                "x": lane_info["end_point"]["x"],
                "y": lane_info["end_point"]["y"],
            },
        }
        info_for_cgw = {
            "secMark": lane_info["secMark"],
            "congestionLanesInfo": {
                "laneId": lane_id,
                "level": lane_info["level"],
                "avgSpeed": int(lane_info["avg_speed"]),
                "startPoint": {
                    "lat": int(lane_info["start_point"]["lat"]),
                    "lon": int(lane_info["start_point"]["lon"]),
                },
                "endPoint": {
                    "lat": int(lane_info["end_point"]["lat"]),
                    "lon": int(lane_info["end_point"]["lon"]),
                },
            },
        }
        return info_for_show, info_for_cgw
