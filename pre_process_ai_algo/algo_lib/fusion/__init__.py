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

"""Fusion Algorithm."""

from itertools import product
import math
import numpy as np
from pre_process_ai_algo.algo_lib.fusion.algorithm import Hungarian
from pre_process_ai_algo.algo_lib.fusion.algorithm import KalmanFilter
from pre_process_ai_algo.algo_lib import utils
from scipy.optimize import leastsq  # type: ignore
import time
from transform_driver.log import Loggings
from typing import Dict
from typing import List

logging = Loggings()


class Base:
    """Super class of Exponential class and Polynomial class."""

    def run(
        self,
        historical_frames: dict,
        latest_frame: dict,
        last_timestamp: int,
        matching_pairs: dict,
        fresh_interval: int,
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class Fusion(Base):
    """Data fusion algorithm.

    Structural logic:
    1. Read historical data and historical pairing ID
    2. Extract conversion data format, judge source number
    3. Pairing IDs in multi-source data through the Hungarian algorithm
    4. Change identification ID for paired track
    5. Apply kalman filter for fusion of target vectors of the same ID
    6. Calculate other fusion parameters
    7. Standard data format, returns the track point at the current moment

    """

    # 类所需内参
    DefaultInterval = 100
    MinTrackLength = 3

    def __init__(
        self, dis_threshold: int = 2, min_track_length: int = MinTrackLength
    ) -> None:
        """Class initialization.

        dis_threshold : int, optional
            The minimum threshold of the parameter Euclidean distance
            to determine whether the target can be paired.
            The default is 2 <m>.
        min_track_length : int, optional
            Minimum trajectory length that can be used for fusion.
            Cannot be less than 3
            The default is 3.

        """
        self._dis_threshold = dis_threshold
        self._min_track_length = min_track_length

    def run(
        self,
        historical_frames: dict,
        latest_frame: dict,
        last_timestamp: int,
        matching_pairs: Dict[str, list] = {},
        fresh_interval: int = DefaultInterval,
    ) -> tuple:
        """External call function.

        Input:
        historical_frames : dict
        It is dict of history track data.

        latest_frame : dict
        It is the latest data obtain from RSU.

        matching_pairs : dict, optional
        It is history data matching pairs dict, same target's IDs
        are stored in the same element.
        The default is {}.

        fresh_interval: int, optional
        It determines the time interval covered by the
        returned fusion data.
        When the track's last time to current time is outside
        of fresh_interval, it will not included in return data.
        DEFAULT_INTERVAL_<ms> = 100

        Output:
        updated_latest_frame:
        The latest frame data after smooth processing, AID format

        last_timestamp:
        Timestamp of current frame data for the next call

        match_pairs:
        Data matching pairs dict, for the next function call

        """
        start_time = time.time()
        id_set, last_timestamp = utils.frames_combination(
            historical_frames, latest_frame, last_timestamp
        )
        self._max_time = last_timestamp
        self._fresh_interval = fresh_interval
        self._match_pairs = matching_pairs
        self._structured_frame: Dict[str, Dict] = {}
        if historical_frames != {}:
            self._source_pkg = historical_frames
            self._format_trans(self._source_pkg, last_timestamp)
        else:
            logging.info("No data input")
            return self._structured_frame, last_timestamp, self._match_pairs

        if self._source_num > 1:
            self._matching()
        elif self._source_num == 1:
            logging.trace(
                "Only 1 source, normalized trajectroies has been sent back"
            )
        elif self._source_num == 0:
            logging.trace("No source data obtained")
            return self._structured_frame, last_timestamp, dict()
        fused_frame = self._fusing()
        self._struct(fused_frame)

        end_time = time.time()
        self._calc_time = end_time - start_time

        return self._structured_frame, last_timestamp, self._match_pairs

    def _format_trans(self, context_frames: dict, last_timestamp: int) -> None:
        # 兼容多设备：增加dict，存储(source, lon, lat)的str = tag
        # 出现新track，检验源tag是否在dict里，如果在说明重复了。
        # 没重复就给dict添加key=tag: only_source = source + 8 * i++
        # 判断len(dict)
        i = 0
        frame_indicator: Dict[str, Dict] = {}  # {label: only_source}
        std_frame: Dict[str, dict] = {}
        for key in sorted(context_frames):  # key = OnlyId
            # non-moter object skip fusion
            # if key not in id_set:
            #     continue
            if context_frames[key][-1]["timeStamp"] < last_timestamp:
                continue
            if context_frames[key][-1]["ptcType"] != "motor":
                self._structured_frame.update(
                    {key: context_frames[key][-1]}
                )  # only add last position
            else:
                track = context_frames[key]
                for refpos in ("refPos_lat", "refPos_lon"):
                    if refpos not in track[0]:
                        track[0][refpos] = 0
                tag = str(
                    (
                        track[0]["source"],
                        track[0]["refPos_lat"],
                        track[0]["refPos_lon"],
                    )
                )
                if tag not in frame_indicator:
                    only_source = track[0]["source"] + i * 8
                    i += 1
                    frame_indicator.update({tag: only_source})
                for row in track:
                    row.update({"typeIndi": 1})
                    for label in (
                        "timeStamp",
                        "secMark",
                        "ptcId",
                        "typeIndi",
                        "x",
                        "y",
                        "speed",
                        "heading",
                        "width",
                        "length",
                    ):
                        if key in std_frame:
                            if label in std_frame[key]:
                                std_frame[key][label].append(row[label])
                            else:
                                std_frame[key].update({label: [row[label]]})
                        else:
                            std_frame[key] = {label: [row[label]]}
                    std_frame[key].setdefault("source", [])
                    std_frame[key]["source"].append(frame_indicator[tag])
        self._source_num = len(frame_indicator)
        self._std_source = std_frame  # key = OnlyId

    def _curve_fitting(self, p, x, y):
        a1, a2, a3 = p
        return a1 * x + a2 * y + a3

    def _fitting_error(self, p, x, y, t):
        err = self._curve_fitting(p, x, y) - t
        return err

    def _pos_extract(self, track: dict) -> list:
        # 计算一条track的时空位置均值
        x = np.array(track["x"]).mean()
        y = np.array(track["y"]).mean()
        t = np.array(track["timeStamp"]).mean()
        return [x, y, t]

    def _motion_extract(self, track: dict) -> list:
        # 计算一个track中的运动特征，最小二乘
        x = np.array(track["x"])
        y = np.array(track["y"])
        t = np.array(track["timeStamp"])
        p0 = [0.1, 0.01, 100]  # 拟合的初始参数设置
        para = leastsq(self._fitting_error, p0, args=(x, y, t))  # 进行拟合
        a, b, t = para[0]
        return [a, b, t]

    def _eucli_dist(self, obj1: list, row1: list) -> float:
        p1 = [row1[2], row1[3], row1[4]]
        p2 = [obj1[1], obj1[2], obj1[3]]
        dis = math.sqrt(sum([(a - b) ** 2 for (a, b) in zip(p1, p2)]))
        return dis

    def _add(self, id1, id2):
        mp = self._match_pairs
        self._match_pairs[id1] += [i for i in mp[id2] if i not in mp[id1]]

    def _matching(self) -> None:
        # Aim to get ID-match_pairs in sources of track
        # ----Get Moving MTX----#
        pos_dict: Dict[int, list] = {}
        for key in self._std_source:
            track = self._std_source[key]
            if len(track["timeStamp"]) < self._min_track_length:
                continue
            pos_feature = self._pos_extract(track)  # 获得时空位置特征
            source_label = track["source"][0]
            pos_dict.setdefault(source_label, [])
            pos_dict[source_label].append([source_label, key] + pos_feature)
        # ----Build 2-side Graph Link----#
        ref_param: List[float] = []  # ['ID', 'xParam', 'yParam','tParam']
        link: Dict[
            str, list
        ] = {}  # link={ID: [ptcID, ptcID],ID:[ptcID,ptcID,ptcID]}
        # -----Hungarian Solve-----#
        hungarian = Hungarian()
        for source_label in pos_dict:
            obj_group = pos_dict[source_label]
            if len(ref_param) == 0:
                for row in obj_group:
                    ref_param.append(row[1:5])
                    self._match_pairs[row[1]] = [row[1]]
                continue
            # source, OnlyId, a, b, t
            for obj0, obj1 in product(obj_group, ref_param):
                if self._eucli_dist(obj1, obj0) < self._dis_threshold:
                    link.setdefault(obj1[0], [])
                    link[obj1[0]].append(obj0[1])
            pairs = hungarian.run(link)
            for obj in obj_group:
                unmatched = True
                for maj_id, sub_id in pairs.items():
                    if maj_id in self._match_pairs:
                        unmatched = False
                        if sub_id in self._match_pairs:
                            self._add(maj_id, sub_id)
                            del self._match_pairs[sub_id]
                            continue
                        elif sub_id not in self._match_pairs[maj_id]:
                            self._match_pairs[maj_id].append(sub_id)
                if unmatched:
                    is_candidate = False
                    for key in self._match_pairs:
                        if obj[1] in self._match_pairs[key]:
                            is_candidate = True
                            break
                    if is_candidate:
                        continue
                    ref_param.append(obj[1:5])
                    self._match_pairs.setdefault(obj[1], [])
                    if obj[1] not in self._match_pairs[obj[1]]:
                        self._match_pairs[obj[1]].append(obj[1])

    def _add_in(self, key: str, aim_frame: dict, candidate: dict) -> dict:
        if key in aim_frame:
            sort = np.array([])  # type: ignore
            for label in (
                "timeStamp",
                "secMark",
                "ptcId",
                "source",
                "typeIndi",
                "x",
                "y",
                "speed",
                "heading",
                "width",
                "length",
            ):
                aim_frame[key][label] += candidate[label]
                if label == "timeStamp":
                    sort = np.argsort(aim_frame[key]["timeStamp"])
                aim_frame[key][label] = list(
                    np.array(aim_frame[key][label])[sort]
                )
        else:
            aim_frame.update({key: candidate})
        return aim_frame

    def _rename_id(self) -> Dict:
        # Unified ID according to match
        aim_frame: Dict[str, dict] = {}
        unmatched = True
        if self._source_num == 1:
            return self._std_source
        for ma_id in self._std_source:
            for key in self._match_pairs:  # ID:[ptcID]
                if ma_id in self._match_pairs[key] or ma_id == key:
                    aim_frame = self._add_in(
                        key, aim_frame, self._std_source[ma_id]
                    )
                    unmatched = False
                    break
            if unmatched:
                aim_frame.update({ma_id: self._std_source[ma_id]})
        return aim_frame

    def _fusing(self) -> list:
        # Unified ID and do kalman fusing
        self._std_source = self._rename_id()  # key=ID: [{ptcId: ptcId}]
        fused_frame = []
        for ID in sorted(self._std_source):
            track = self._std_source[ID]
            if len(track["timeStamp"]) > self._min_track_length:
                kalman = KalmanFilter()
                x, y, t = kalman.run(
                    track["x"], track["y"], track["timeStamp"]
                )
                data_source = 7
            else:
                x, y = track["x"], track["y"]
                data_source = track["source"][-1]
            if track["timeStamp"][-1] < self._max_time - self._fresh_interval:
                continue
            width = np.mean(track["width"])
            length = np.mean(track["length"])
            heading = track["heading"][-1]
            speed = track["speed"][-1]
            fused_frame.append(
                [
                    track["secMark"][-1],
                    ID,
                    data_source,
                    1,
                    x[-1],
                    y[-1],
                    speed,
                    heading,
                    width,
                    length,
                ]
            )
        return fused_frame

    def _update_structed(self, maPtcId, frame) -> tuple:
        structed = {}
        found = False
        if maPtcId in self._source_pkg:  # ptcId
            dic = self._source_pkg[maPtcId][-1]
            structed.update(dic)
            structed.update(
                {
                    "secMark": int(frame[0]),
                    "source": int(frame[2] % 8),
                    "x": float(frame[4]),
                    "y": float(frame[5]),
                    "speed": int(frame[6]),
                    "heading": int(frame[7]),
                    "width": int(frame[8]),
                    "length": int(frame[9]),
                }
            )
            found = True
        return found, structed

    def _struct(self, fused_frame) -> Dict:
        for frame in fused_frame:
            key = frame[1]  # key = ID
            structed = {}
            if len(self._match_pairs) and (key in self._match_pairs):
                for maPtcId in self._match_pairs[key]:
                    found, structed = self._update_structed(maPtcId, frame)
                    if found:
                        break
            else:
                found, structed = self._update_structed(frame[1], frame)
            self._structured_frame.update({key: structed})
        return self._structured_frame
