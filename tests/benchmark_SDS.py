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

"""Plot benchmark curves of SDS algorithm."""

import copy
import matplotlib.pyplot as plt
from post_process_algo import post_process
from scenario_algo.algo_lib import collision_warning
from scenario_algo.algo_lib import sensor_data_sharing
import time

# FPS = 10 interval = 100 ms
# 需 collision_warning 中改： if len(filtered) <= 2:
rsu_id = "R328328"
convert_info = [post_process.TfMap[rsu_id]] + [
    post_process.XOrigin[rsu_id],
    post_process.YOrigin[rsu_id],
]
sensor_pos = post_process.rsu_info[rsu_id]["pos"]
ctx_frames = {
    "ab00000de": [
        {
            "global_track_id": "ab00000de",
            "secMark": 49000,
            "timeStamp": 49000,
            "ptcType": "motor",
            "x": 74.69,
            "y": 52.92,
            "lat": 319353292,
            "lon": 1188217469,
            "speed": 2.382780797508647,
            "heading": 283.15000000000003,
            "lane": 2,
        },
        {
            "global_track_id": "ab00000de",
            "secMark": 49033,
            "timeStamp": 49033,
            "ptcType": "motor",
            "x": 74.61,
            "y": 54.15,
            "lat": 319353415,
            "lon": 1188217461,
            "speed": 2.3319426892555706,
            "heading": 284.075,
            "lane": 2,
        },
        {
            "global_track_id": "ab00000de",
            "secMark": 49066,
            "timeStamp": 49066,
            "ptcType": "motor",
            "x": 74.53,
            "y": 52.90,
            "lat": 319353290,
            "lon": 1188217453,
            "speed": 2.44178323861912,
            "heading": 284.77500000000003,
            "lane": 2,
        },
    ],
    "ab00001de": [
        {
            "global_track_id": "ab00001de",
            "secMark": 49000,
            "timeStamp": 49000,
            "ptcType": "motor",
            "x": 79.53,
            "y": 54.17,
            "lat": 319353417,
            "lon": 1188217953,
            "speed": 2.3189334769512975,
            "heading": 279.95,
            "lane": 1,
        },
        {
            "global_track_id": "ab00001de",
            "secMark": 49033,
            "timeStamp": 49033,
            "ptcType": "motor",
            "x": 79.44,
            "y": 54.15,
            "lat": 319353415,
            "lon": 1188217944,
            "speed": 2.367288382851602,
            "heading": 280.40000000000003,
            "lane": 1,
        },
        {
            "global_track_id": "ab00001de",
            "secMark": 49066,
            "timeStamp": 49066,
            "ptcType": "motor",
            "x": 79.53,
            "y": 54.17,
            "lat": 319353415,
            "lon": 1188217936,
            "speed": 2.367288382851602,
            "heading": 280.7625,
            "lane": 1,
        },
    ],
    "ab00002de": [
        {
            "global_track_id": "ab00002de",
            "secMark": 49000,
            "timeStamp": 49000,
            "ptcType": "motor",
            "x": 82.72,
            "y": 53.14,
            "lat": 319353314,
            "lon": 1188218272,
            "speed": 1.3457216790860351,
            "heading": 256.175,
            "lane": 2,
        },
        {
            "global_track_id": "ab00002de",
            "secMark": 49033,
            "timeStamp": 49033,
            "ptcType": "motor",
            "x": 82.67,
            "y": 53.14,
            "lat": 319353314,
            "lon": 1188218267,
            "speed": 1.364691834834067,
            "heading": 256.25,
            "lane": 2,
        },
        {
            "global_track_id": "ab00002de",
            "secMark": 49066,
            "timeStamp": 49066,
            "ptcType": "motor",
            "x": 82.63,
            "y": 53.15,
            "lat": 319353315,
            "lon": 1188218263,
            "speed": 1.3944767505214746,
            "heading": 256.35,
            "lane": 2,
        },
    ],
}
crt_frame = {
    "ab00000de": {
        "global_track_id": "ab00000de",
        "secMark": 49100,
        "timeStamp": 49100,
        "ptcType": "motor",
        "x": 74.45,
        "y": 52.89,
        "lat": 319353289,
        "lon": 1188217445,
        "speed": 2.505984561026474,
        "heading": 285.2625,
        "lane": 2,
    },
    "ab00001de": {
        "global_track_id": "ab00001de",
        "secMark": 49100,
        "timeStamp": 49100,
        "ptcType": "motor",
        "x": 79.28,
        "y": 53.15,
        "lat": 319353414,
        "lon": 1188217928,
        "speed": 2.3965827991135984,
        "heading": 281.05,
        "lane": 1,
    },
    "ab00002de": {
        "global_track_id": "ab00002de",
        "secMark": 49100,
        "timeStamp": 49100,
        "ptcType": "motor",
        "x": 82.58,
        "y": 53.15,
        "lat": 319353315,
        "lon": 1188218258,
        "speed": 1.4318766343495333,
        "heading": 256.4875,
        "lane": 2,
    },
}
last_ts = 49066
msg_VIR = {
    "msgCnt": "1",
    "id": "ab00001de",
    "refPos": {"lon": 1188217928, "lat": 319353414, "ele": 100},
    "secMark": 49100,
    "timeStamp": 1653016849100,
    "intAndReq": {
        "reqs": {
            "reqID": 1,
            "status": 2,
            "reqPriority": "B11100000",
            "targetRSU": "R328328",
            "info": {
                "sensorSharing": {
                    "detectArea": {
                        "activePath": [
                            {"lon": 1188219474, "lat": 319353248, "ele": 100},
                            {"lon": 1188219459, "lat": 319353249, "ele": 100},
                            {"lon": 1188219444, "lat": 319353250, "ele": 100},
                            {"lon": 1188219428, "lat": 319353251, "ele": 100},
                            {"lon": 1188219412, "lat": 319353252, "ele": 100},
                        ]
                    }
                }
            },
            "lifeTime": 50,
        }
    },
}


def expand_data(origin_data):
    """Expand data based on original data."""
    new_guid_number = len(origin_data)
    copied_guid_number = new_guid_number - 3
    new_guid = "ab" + str(new_guid_number).zfill(5) + "de"
    copied_guid = "ab" + str(copied_guid_number).zfill(5) + "de"
    new_obj_info = copy.deepcopy(origin_data[copied_guid])
    origin_data[new_guid] = new_obj_info
    for i in new_obj_info:
        i["x"] += 100
        i["y"] += 100
        i["global_track_id"] = new_guid
    return origin_data


def expand_current_data(origin_data):
    """Expand data based on original data."""
    new_guid_number = len(origin_data)
    copied_guid_number = new_guid_number - 3
    new_guid = "ab" + str(new_guid_number).zfill(5) + "de"
    copied_guid = "ab" + str(copied_guid_number).zfill(5) + "de"
    new_obj_info = copy.deepcopy(origin_data[copied_guid])

    new_obj_info["x"] += 100
    new_obj_info["y"] += 100
    new_obj_info["global_track_id"] = new_guid
    origin_data[new_guid] = new_obj_info
    return origin_data


def calc_sds_eff_fps(convert_info, context_frames, current_frame, msg_VIR):
    """Count times algorithm can run in specific interval."""
    begin_time = time.monotonic_ns()
    count_process_times = 0
    cw_exp = collision_warning.CollisionWarning()
    sexp = sensor_data_sharing.SensorDataSharing()
    while (time.monotonic_ns() - begin_time) / 1000000000 <= process_interval:
        context_frames_new = copy.deepcopy(context_frames)
        current_frame_new = copy.deepcopy(current_frame)
        _, _, _, motors_trajs, vptc_trajs = cw_exp.run(
            context_frames_new, current_frame_new, last_ts
        )
        _ = sexp.run(
            motors_trajs, vptc_trajs, {}, msg_VIR, sensor_pos, convert_info
        )
        count_process_times += 1
    return count_process_times


def calc_sds_eff_time(convert_info, context_frames, current_frame, msg_VIR):
    """Record the time spent processing a frame of data."""
    begin_time = time.monotonic_ns()
    cw_exp = collision_warning.CollisionWarning()
    sexp = sensor_data_sharing.SensorDataSharing()
    context_frames_new = copy.deepcopy(context_frames)
    current_frame_new = copy.deepcopy(current_frame)
    _, _, _, motors_trajs, vptc_trajs = cw_exp.run(
        context_frames_new, current_frame_new, last_ts
    )
    _ = sexp.run(
        motors_trajs, vptc_trajs, {}, msg_VIR, sensor_pos, convert_info
    )
    process_time = time.monotonic_ns() - begin_time
    return process_time / 1000000


def draw_sds_fps(x, y):
    """Draw the curve of fps result."""
    plt.plot(x, y)
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (times/second)", fontsize=13)
    plt.title("SDS Algorithm Benchmark", fontsize=15)


def draw_sds_time(x, y):
    """Draw the curve of time result."""
    plt.plot(x, y)
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (milliseconds/frame)", fontsize=13)
    plt.title("SDS Algorithm Benchmark", fontsize=15)


max_id_amount = 100
benchmark_point_interval = 5
process_interval = 1  # s

"""fps"""


def draw_benchmark_fps(convert_info, context_frames1, current_frame1, msg_VIR):
    """Drawing fps curve."""
    benchmark_point_x = []
    benchmark_point_y = []
    while len(context_frames1) < max_id_amount:
        expand_data(context_frames1)
        expand_current_data(current_frame1)
        if len(context_frames1) % benchmark_point_interval == 0:
            benchmark_point_x.append(len(context_frames1))
            benchmark_point_y.append(
                calc_sds_eff_fps(
                    convert_info, context_frames1, current_frame1, msg_VIR
                )
            )
    plt.figure(figsize=(8, 5))
    draw_sds_fps(benchmark_point_x, benchmark_point_y)
    plt.savefig("sds_algo_benchmark_fps.png", dpi=300)
    plt.savefig("sds_algo_benchmark_fps.svg")
    plt.show()


ctx_frames1 = copy.deepcopy(ctx_frames)
crt_frame1 = copy.deepcopy(crt_frame)
draw_benchmark_fps(convert_info, ctx_frames1, crt_frame1, msg_VIR)

"""time"""


def draw_benchmark_time(
    convert_info, context_frames2, current_frame2, msg_VIR
):
    """Drawing time curve."""
    benchmark_point_x = []
    benchmark_point_y = []
    while len(context_frames2) < max_id_amount:
        expand_data(context_frames2)
        expand_current_data(current_frame2)
        if len(context_frames2) % benchmark_point_interval == 0:
            benchmark_point_x.append(len(context_frames2))
            benchmark_point_y.append(
                calc_sds_eff_time(
                    convert_info, context_frames2, current_frame2, msg_VIR
                )
            )
    plt.figure(figsize=(8, 5))
    draw_sds_time(benchmark_point_x, benchmark_point_y)
    plt.savefig("sds_algo_benchmark_time.png", dpi=300)
    plt.savefig("sds_algo_benchmark_time.svg")
    plt.show()


ctx_frames2 = copy.deepcopy(ctx_frames)
crt_frame2 = copy.deepcopy(crt_frame)
draw_benchmark_time(convert_info, ctx_frames2, crt_frame2, msg_VIR)
