"""General shared utilities."""

from transform_driver import consts

MaxSecMark = consts.MaxSecMark
# 以下参数根据算法所需数据量确定，算法最多需要2s的历史数据，大于2.5s的数据即可删除
HistoricalInterval = 1600  # 同一id容纳的历史数据时间范围
UpdateInterval = 1600  # 某一id可容忍的不更新数据的时间范围


def frame_delete(context_frames: dict, last_timestamp: int) -> None:
    """Delete invalid frame data in historical data."""
    # 删除同一guid过老旧数据，以及删除过久没有更新过的guid所有数据
    guid_list = list(context_frames.keys())
    for guid in guid_list:
        if (
            last_timestamp - context_frames[guid][0]["timeStamp"]
            > HistoricalInterval
        ):
            del context_frames[guid][0]
        if (
            len(context_frames[guid]) == 0
            or last_timestamp - context_frames[guid][-1]["timeStamp"]
            > UpdateInterval
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
                obj_info["timeStamp"] += MaxSecMark
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


def get_current_frame(frames: dict, last_timestamp: int) -> dict:
    """Split current frame data from historical frame data."""
    # 将最新帧数据从历史数据中提取出来
    latest_frame = {}
    for obj_info in frames.values():
        if obj_info[-1]["timeStamp"] == last_timestamp:
            obj_id = obj_info[-1]["global_track_id"]
            latest_frame[obj_id] = obj_info[-1]
    return latest_frame
