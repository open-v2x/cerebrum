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

"""Scenario of OverSpeed Warning."""

import numpy as np
import pandas as pd
from post_process_algo import post_process
from pre_process_ai_algo.algo_lib import utils as process_tools
from scenario_algo.algo_lib import utils
from typing import List


MinDataDuration = 1.5  # 至少有多少秒的数据才计算车辆的动力学信息


class Base:
    """Super class of overspeed warning class."""

    def run(
        self,
        context_frames: dict,
        current_frame: dict,
        last_timestamp: int,
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class OverspeedWarning(Base):
    """Scenario of OverSpeed Warning."""

    def run(
        self,
        context_frames: dict,
        current_frame: dict,
        last_timestamp: int,
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
        overspeed_warning_message:
        Overspeed warning message for broadcast, osw format

        last_timestamp:
        Timestamp of current frame data for the next call

        """
        self._show_info: List[dict] = []
        self._overspeed_warning_message: List[dict] = []
        self._current_frame = current_frame

        id_set, last_timestamp = process_tools.frames_combination(
            context_frames, self._current_frame, last_timestamp
        )

        # 只检查机动车是否超速
        check_ptc = ["motors"]
        ptc_info: dict = {"motors": {}}
        # 分别计算机动车、非机动车、行人的运动学信息，用于检查车辆超速情况
        motors, non_motors, pedestrians = self._filter_ptcs(
            context_frames, last_timestamp, id_set
        )
        for ptc_type in check_ptc:
            ptc_info[ptc_type + "_kinematics"] = getattr(
                self, "_prepare_{}_kinematics".format(ptc_type)
            )(locals()[ptc_type])

        current_df = pd.DataFrame(ptc_info["motors_kinematics"]).T
        if current_df.empty:
            return (
                self._overspeed_warning_message,
                self._show_info,
                last_timestamp,
            )
        current_df["speed"] = current_df["speed"].apply(
            lambda x: int(x / 0.02)
        )
        # 获取最高限速
        current_df["vehicleMaxSpeed"] = current_df["lane"].apply(
            self._get_max_speed_limit
        )
        current_df = current_df.dropna(
            axis=0, subset=["vehicleMaxSpeed"]
        )  # 删除指定列中有缺失值的那一行数据
        df = current_df[
            np.where(
                current_df["speed"]
                > current_df["vehicleMaxSpeed"],  # type: ignore
                True,
                False,
            )
        ]  # type: ignore
        df.apply(self._build_osw_event, axis=1)
        return (
            self._overspeed_warning_message,
            self._show_info,  # type: ignore
            last_timestamp,
        )

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
                "speed": mot[-1]["speed"],
                "heading": mot[-1]["heading"],
                "width": mot[-1]["width"],
                "length": mot[-1]["length"],
                "height": mot[-1]["height"],
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

    def _get_max_speed_limit(self, lane):
        return post_process.speed_limits.get(lane, {}).get(
            "vehicleMaxSpeed", None
        )

    def _build_osw_event(self, df_res):
        info_for_show = {
            "ego": df_res["ptcId"],
            "ego_current_point": [df_res["x"], df_res["y"]],
        }

        info_for_osw = {
            "secMark": df_res["secMark"],
            "egoInfo": {
                "egoId": df_res["ptcId"],
                "egoPos": {
                    "lat": int(df_res["lat"]),
                    "lon": int(df_res["lon"]),
                },
                "speed": df_res["speed"],
                "heading": df_res["heading"],
                "width": df_res["width"],
                "length": df_res["length"],
                "height": df_res["height"],
            },
        }

        self._show_info.append(info_for_show)
        self._overspeed_warning_message.append(info_for_osw)
