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

"""Complement Algorithm.

1. Interpolation
2. Predicted by Long Short-term Memory Network

"""

import math
import numpy as np
import os
from pre_process_ai_algo.algo_lib.complement.lstm.corenet import RegLSTM
from pre_process_ai_algo.algo_lib import utils
import torch
from typing import Any
from typing import Union


class Base:
    """Super class of Interpolation class and LstmPredict class."""

    def run(
        self, context_frames: dict, current_frame: dict, last_timestamp: int
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class Interpolation(Base):
    """Interpolation Completion Algorithm.

    Structural logic:
    1. Combine historical frame data and current frame data
    2. Determine the moment that needs to be completed according to the delay
       time
    3. Determine whether the front and rear track speeds of the missing time
       are reasonable
    4. Complete the missing trajectory point by interpolation function

    """

    def __init__(
        self,
        lag_time: int = 200,  # ms 至少保证雷达或视频可延时 1-2 帧
        max_speed_motor: int = 120,  # km/h
        max_speed_non_motor: int = 15,  # km/h
        max_speed_pedestrian: int = 5,  # km/h
    ) -> None:
        """Class initialization.

        lag_time:
        The required lag time in order to obtain the before and after
        trajectories of the missing points

        max_speed_motor:
        The speed of the motor's maximum allowable completion point

        max_speed_non_motor:
        The speed of the non_motor's maximum allowable completion point

        max_speed_pedestrian:
        The speed of the pedestrian's maximum allowable completion point

        """
        self._lag_time = lag_time
        # 延误帧数
        self._speed_coefficient = 3.6
        # 行人最大时速，若需补全的数据超过此时速，则判为异常
        self._speed_dict = {
            "motor": max_speed_motor / self._speed_coefficient,
            "non-motor": max_speed_non_motor / self._speed_coefficient,
            "pedestrian": max_speed_pedestrian / self._speed_coefficient,
        }

    def run(
        self, context_frames: dict, current_frame: dict, last_timestamp: int
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
        updated_latest_frame:
        The latest frame data after completion processing, AID format

        last_timestamp:
        Timestamp of current frame data for the next call

        """
        _, last_timestamp = utils.frames_combination(
            context_frames, current_frame, last_timestamp
        )
        return (
            self._handle_interpolation(
                context_frames, self._find_delay_sec_mark(context_frames)
            ),
            last_timestamp,
        )

    def _find_nearest(self, array: list, value: int) -> int:
        # 找出需要做补全指定帧号下指定id的下标
        for index, j in enumerate(array):
            if j - value >= 0:
                return index
        return index

    def _is_frame_valid(
        self, obj_info: dict, index: int, delay_sec_mark: int
    ) -> bool:
        if obj_info[index]["timeStamp"] == delay_sec_mark:
            return False
        # 判断id下一次再出现时是否是位移过远，是否是无效数据
        dis_x = obj_info[index]["x"] - obj_info[index - 1]["x"]
        dis_y = obj_info[index]["y"] - obj_info[index - 1]["y"]
        # 1000 用于毫秒转秒，计算速度
        time_interval = (
            obj_info[index]["timeStamp"] - obj_info[index - 1]["timeStamp"]
        ) / 1000
        speed = math.hypot(dis_x, dis_y) / time_interval
        speed_max = self._speed_dict[obj_info[index]["ptcType"]]
        return speed_max > speed

    def _complete_obj(
        self, objs_info: list, index: int, delay_sec_mark: int
    ) -> None:
        # 补全指定的帧号下指定 id的轨迹点
        objs_info.insert(index, objs_info[index].copy())
        for i in ("x", "y"):
            objs_info[index][i] = objs_info[index - 1][i] + (
                objs_info[index + 1][i] - objs_info[index - 1][i]
            ) * (delay_sec_mark - objs_info[index - 1]["timeStamp"]) / (
                objs_info[index + 1]["timeStamp"]
                - objs_info[index - 1]["timeStamp"]
            )
        objs_info[index]["timeStamp"] = delay_sec_mark
        objs_info[index]["secMark"] = delay_sec_mark % utils.MaxSecMark

    def _find_delay_sec_mark(self, frames: dict) -> int:
        # 找到 delay_sec_mark，并更新原 frames的 secmark
        max_sec = 0
        for objs_info in frames.values():
            max_sec_each_id = objs_info[-1]["timeStamp"]
            max_sec = max(max_sec_each_id, max_sec)
        delay_sec_mark = max_sec
        for objs_info in frames.values():
            for fr in objs_info:
                if fr["timeStamp"] >= max_sec - self._lag_time:
                    delay_sec_mark = min(fr["timeStamp"], delay_sec_mark)
                    break
        return delay_sec_mark

    def _handle_interpolation(self, frames: dict, delay_sec_mark: int) -> dict:
        # 判断是否需要做补全，并调相应函数做补全处理
        updated_latest_frame = {}
        for objs_info in frames.values():
            sec_mark_list = [fr["timeStamp"] for fr in objs_info]
            index = self._find_nearest(sec_mark_list, delay_sec_mark)
            if index != 0:
                if self._is_frame_valid(objs_info, index, delay_sec_mark):
                    self._complete_obj(objs_info, index, delay_sec_mark)
                for i in range(len(objs_info) - 1, -1, -1):
                    if objs_info[i]["timeStamp"] == delay_sec_mark:
                        obj_id = objs_info[i]["global_track_id"]
                        updated_latest_frame[obj_id] = objs_info[i]
        return updated_latest_frame


class LstmPredict(Base):
    """Interpolation Completion Algorithm.

    Structural logic:
    1. Combine historical frame data and current frame data
    2. Determine the moment that needs to be completed according to the delay
       time
    3. Determine whether the front and rear track speeds of the missing time
       are reasonable
    4. Complete the missing trajectory point by Long Short-term Memory Network

    """

    InputFeatureNum = 3
    OutputFeaturesNum = 2
    HistoryNum = 3
    HiddenSize = 4
    Layers = 4
    TimeRate = 0.001  # 1 timeStamp = 0.001 second

    def __init__(
        self,
        model_path: str = os.path.dirname(__file__) + "/lstm/lstm.pkl",
        const_stand: int = 200,
        history_num: int = HistoryNum,
        layers: int = Layers,
        hidden_sz: int = HiddenSize,
        bidirectional: bool = True,
        lag_time: int = 200,  # ms 至少保证雷达或视频可延时 1-2 帧
        max_speed_motor: int = 120,  # km/h
        max_speed_non_motor: int = 15,  # km/h
        max_speed_pedestrian: int = 5,  # km/h
    ) -> None:
        """Class initialization.

        model_path:
        Weight address of LSTM

        const_stand:
        Constant required for normalization

        history_num:
        Number of historical trajectory points used for prediction

        layers:
        The number of layers of LSTM

        hidden_sz:
        The hidden size of LSTM

        bidirectional:
        whether change to bidirectional lstm

        lag_time:
        The required lag time in order to obtain the before and after
        trajectories of the missing points

        max_speed_motor:
        The speed of the motor's maximum allowable completion point

        max_speed_non_motor:
        The speed of the non_motor's maximum allowable completion point

        max_speed_pedestrian:
        The speed of the pedestrian's maximum allowable completion point

        """
        self._const_stand = const_stand
        self._lag_time = lag_time
        self._speed_coefficient = 3.6
        self._speed_dict = {
            "motor": max_speed_motor / self._speed_coefficient,
            "non-motor": max_speed_non_motor / self._speed_coefficient,
            "pedestrian": max_speed_pedestrian / self._speed_coefficient,
        }
        self._his_num = history_num
        in_feature = self.InputFeatureNum
        self._out_feature = self.OutputFeaturesNum
        self._lstm_model = RegLSTM(
            in_feature * history_num,
            hidden_size=hidden_sz,
            output_size=self._out_feature,
            num_layers=layers,
            bidirectional=bidirectional,
        )
        self._lstm_model.load_state_dict(
            torch.load(model_path, map_location=lambda storage, loc: storage)
        )  # load model

    def run(
        self, context_frames: dict, current_frame: dict, last_timestamp: int
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
        updated_latest_frame:
        The latest frame data after completion processing, AID format

        last_timestamp:
        Timestamp of current frame data for the next call

        """
        _, last_timestamp = utils.frames_combination(
            context_frames, current_frame, last_timestamp
        )
        # 处理断裂轨迹
        return (
            self._handle_lstm(
                context_frames, self._find_delay_sec_mark(context_frames)
            ),
            last_timestamp,
        )

    def _find_nearest(self, array: list, value: int) -> int:
        # 找出需要做补全指定帧号下指定id的下标
        for index, j in enumerate(array):
            if j - value >= 0:
                return index
        return index

    def _is_frame_valid(
        self, obj_info: dict, index: int, delay_sec_mark: int
    ) -> bool:
        if obj_info[index]["timeStamp"] == delay_sec_mark:
            return False
        # 判断id下一次再出现时是否是位移过远，是否是无效数据
        dis_x = obj_info[index]["x"] - obj_info[index - 1]["x"]
        dis_y = obj_info[index]["y"] - obj_info[index - 1]["y"]
        # 1000 用于毫秒转秒，计算速度
        time_interval = (
            obj_info[index]["timeStamp"] - obj_info[index - 1]["timeStamp"]
        ) / 1000
        speed = math.hypot(dis_x, dis_y) / time_interval
        speed_max = self._speed_dict[obj_info[index]["ptcType"]]
        return speed_max > speed

    def _lstm_predict(
        self, objs_info: list, index: int, delay_sec_mark: int
    ) -> None:
        # 补全指定的帧号下指定 id在idx除轨迹点xy
        objs_info.insert(index, objs_info[index].copy())
        features: Union[Any] = []
        for i in range(self._his_num - 1, -1, -1):
            row = []
            for k in ("x", "y", "timeStamp"):
                row.append(objs_info[index - i][k])
            features.append(row)
        features = np.array(features).astype(np.float64)
        start_time = int(features[0, 2])
        features[:, 2] = (features[:, 2] - start_time) * self.TimeRate
        features[:, 0:2] = features[:, 0:2] / self._const_stand
        features = features.reshape(1, -1)
        test_x = torch.from_numpy(features).type(  # type: ignore
            torch.FloatTensor
        )
        # test_x = features.type(torch.FloatTensor)
        test_y = self._lstm_model(test_x)
        test_y = test_y.view(-1, self._out_feature).data.numpy()
        predict_pos = test_y[0] * self._const_stand
        objs_info[index]["x"], objs_info[index]["y"] = predict_pos
        objs_info[index]["x"] = float(objs_info[index]["x"])
        objs_info[index]["y"] = float(objs_info[index]["y"])
        objs_info[index]["timeStamp"] = delay_sec_mark
        objs_info[index]["secMark"] = delay_sec_mark % utils.MaxSecMark

    def _find_delay_sec_mark(self, frames: dict) -> int:
        # 找到 delay_sec_mark，并更新原 frames的 secmark
        max_sec = 0
        for objs_info in frames.values():
            max_sec_each_id = objs_info[-1]["timeStamp"]
            max_sec = max(max_sec_each_id, max_sec)
        delay_sec_mark = max_sec
        for objs_info in frames.values():
            for fr in objs_info:
                if fr["timeStamp"] >= max_sec - self._lag_time:
                    delay_sec_mark = min(fr["timeStamp"], delay_sec_mark)
                    break
        return delay_sec_mark

    def _handle_lstm(self, frames: dict, delay_sec_mark: int) -> dict:
        # 判断是否需要做补全，并调相应函数做补全处理
        updated_latest_frame = {}
        for objs_info in frames.values():
            sec_mark_list = [fr["timeStamp"] for fr in objs_info]
            index = self._find_nearest(sec_mark_list, delay_sec_mark)
            if index != 0:
                if self._is_frame_valid(objs_info, index, delay_sec_mark):
                    self._lstm_predict(objs_info, index, delay_sec_mark)
                for i in range(len(objs_info) - 1, -1, -1):
                    if objs_info[i]["timeStamp"] == delay_sec_mark:
                        obj_id = objs_info[i]["global_track_id"]
                        updated_latest_frame[obj_id] = objs_info[i]
        return updated_latest_frame
