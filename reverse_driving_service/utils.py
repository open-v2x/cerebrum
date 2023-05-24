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
"""utils."""
from reverse_driving_service import constants


def frame_delete(context_frames: dict, last_timestamp: int) -> None:
    """Delete invalid frame data in historical data."""
    # 删除同一guid过老旧数据，以及删除过久没有更新过的guid所有数据
    guid_list = list(context_frames.keys())
    for guid in guid_list:
        if (
            last_timestamp - context_frames[guid][0]["timeStamp"]
            > constants.HISTORICAL_INTERVAL
        ):
            del context_frames[guid][0]
        if (
            len(context_frames[guid]) == 0
            or last_timestamp - context_frames[guid][-1]["timeStamp"]
            > constants.UPDATE_INTERVAL
        ):
            del context_frames[guid]


def frames_combination(
    context_frames: dict, current_frame: dict, last_timestamp: int
) -> tuple:
    """Combine historical frame data and current frame data."""
    # 把最新帧数据添加到历史数据中
    # 同时重置时间戳，保证时间戳恒增
    # latest_id_set 用于帮助算法判断那些id没有被更新，从而不参与算法计算
    if len(current_frame) == 0:
        return set(), last_timestamp
    # 如果历史数据不为空
    if context_frames:
        latest_id_set = set()
        for guid, obj_info in current_frame.items():
            # 记录最新帧出现的目标id
            latest_id_set.add(guid)
            obj_info["timeStamp"] = obj_info["secMark"]
            while obj_info["timeStamp"] < last_timestamp:
                obj_info["timeStamp"] += constants.MAX_SEC_MARK
            context_frames.setdefault(guid, [])
            if (
                len(context_frames[guid])
                and context_frames[guid][-1]["timeStamp"]
                == obj_info["timeStamp"]
            ):
                context_frames[guid][-1] = obj_info
            else:
                context_frames[guid].append(obj_info)
            current_sec_mark = obj_info["timeStamp"]
        last_timestamp = current_sec_mark
        frame_delete(context_frames, last_timestamp)
        return latest_id_set, last_timestamp
    # 如果历史数据为空，直接添加
    latest_id_set = set()
    for guid, obj_info in current_frame.items():
        last_timestamp = obj_info["timeStamp"] = obj_info["secMark"]
        context_frames[guid] = [obj_info]
        latest_id_set.add(guid)
    return latest_id_set, last_timestamp


def differentiate(x: list, t: list) -> list:
    """Difference-Based Derivative Calculation Method."""
    if len(x) > len(t):
        raise ValueError("length mismatched")
    if len(x) <= 1:
        raise ValueError("length of x must be greater than 1")
    return [(x[i + 1] - x[i]) / (t[i + 1] - t[i]) for i in range(len(x) - 1)]


def mean(x: list) -> float:
    """Mean calculation method."""
    if len(x) == 0:
        raise ValueError("x cannot be empty")
    return sum(x) / len(x)
