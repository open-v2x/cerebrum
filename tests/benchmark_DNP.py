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

"""Plot benchmark curves of DNP algorithm."""

import copy
import matplotlib.pyplot as plt
from scenario_algo.algo_lib import do_not_pass_warning
import time

# FPS = 10 interval = 100 ms
rsu_id = "R328328"

ctx_frames = {
    "ab00000de": [
        {
            "global_track_id": "ab00000de",
            "secMark": 49000,
            "timeStamp": 1653016849000,
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
            "timeStamp": 1653016849033,
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
            "timeStamp": 1653016849066,
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
            "timeStamp": 1653016849000,
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
            "timeStamp": 1653016849033,
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
            "timeStamp": 1653016849066,
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
            "timeStamp": 1653016849000,
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
            "timeStamp": 1653016849033,
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
            "timeStamp": 1653016849066,
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
        "timeStamp": 1653016849100,
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
        "timeStamp": 1653016849100,
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
        "timeStamp": 1653016849100,
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
msg_VIR = {
    "msgCnt": "2",
    "id": "56.0",
    "refPos": {"lon": 1188221288, "lat": 319353060, "ele": 100},
    "secMark": 51366,
    "timeStamp": 1653016791366,
    "intAndReq": {
        "currentBehavior": 1,
        "reqs": {
            "reqID": 2,
            "status": 2,
            "targetRSU": "100001",
            "info": {
                "retrograde": {
                    "upstreamNode": "",
                    "downstreamNode": "",
                    "targetLane": 1,
                }
            },
            "lifeTime": 500,
        },
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


def calc_dnp_eff_fps(rsu_id, context_frames, current_frame, msg_VIR):
    """Count times algorithm can run in specific interval."""
    begin_time = time.monotonic_ns()
    count_process_times = 0
    sexp = do_not_pass_warning.DoNotPass()
    while (time.monotonic_ns() - begin_time) / 1000000000 <= process_interval:
        context_frames_new = copy.deepcopy(context_frames)
        current_frame_new = copy.deepcopy(current_frame)
        _ = sexp.run(rsu_id, context_frames_new, current_frame_new, msg_VIR)
        count_process_times += 1
    return count_process_times


def calc_dnp_eff_time(rsu_id, context_frames, current_frame, msg_VIR):
    """Record the time spent processing a frame of data."""
    begin_time = time.monotonic_ns()
    sexp = do_not_pass_warning.DoNotPass()
    context_frames_new = copy.deepcopy(context_frames)
    current_frame_new = copy.deepcopy(current_frame)
    _ = sexp.run(rsu_id, context_frames_new, current_frame_new, msg_VIR)
    process_time = time.monotonic_ns() - begin_time
    return process_time / 1000000


def draw_dnp_fps(x, y):
    """Draw the curve of fps result."""
    plt.plot(x, y)
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (times/second)", fontsize=13)
    plt.title("DNP Algorithm Benchmark", fontsize=15)


def draw_dnp_time(x, y):
    """Draw the curve of time result."""
    plt.plot(x, y)
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (milliseconds/frame)", fontsize=13)
    plt.title("DNP Algorithm Benchmark", fontsize=15)


max_id_amount = 100
benchmark_point_interval = 5
process_interval = 1  # s

"""fps"""


def draw_benchmark_fps(rsu_id, context_frames1, current_frame1, msg_VIR):
    """Drawing fps curve."""
    benchmark_point_x = []
    benchmark_point_y = []
    while len(context_frames1) < max_id_amount:
        expand_data(context_frames1)
        expand_current_data(current_frame1)
        if len(context_frames1) % benchmark_point_interval == 0:
            benchmark_point_x.append(len(context_frames1))
            benchmark_point_y.append(
                calc_dnp_eff_fps(
                    rsu_id, context_frames1, current_frame1, msg_VIR
                )
            )
    plt.figure(figsize=(8, 5))
    draw_dnp_fps(benchmark_point_x, benchmark_point_y)
    plt.savefig("dnp_algo_benchmark_fps.png", dpi=300)
    plt.savefig("dnp_algo_benchmark_fps.svg")
    plt.show()


ctx_frames1 = copy.deepcopy(ctx_frames)
crt_frame1 = copy.deepcopy(crt_frame)
draw_benchmark_fps(rsu_id, ctx_frames1, crt_frame1, msg_VIR)

"""time"""


def draw_benchmark_time(rsu_id, context_frames2, current_frame2, msg_VIR):
    """Drawing time curve."""
    benchmark_point_x = []
    benchmark_point_y = []
    while len(context_frames2) < max_id_amount:
        expand_data(context_frames2)
        expand_current_data(current_frame2)
        if len(context_frames2) % benchmark_point_interval == 0:
            benchmark_point_x.append(len(context_frames2))
            benchmark_point_y.append(
                calc_dnp_eff_time(
                    rsu_id, context_frames2, current_frame2, msg_VIR
                )
            )
    plt.figure(figsize=(8, 5))
    draw_dnp_time(benchmark_point_x, benchmark_point_y)
    plt.savefig("dnp_algo_benchmark_time.png", dpi=300)
    plt.savefig("dnp_algo_benchmark_time.svg")
    plt.show()


ctx_frames2 = copy.deepcopy(ctx_frames)
crt_frame2 = copy.deepcopy(crt_frame)
draw_benchmark_time(rsu_id, ctx_frames2, crt_frame2, msg_VIR)
