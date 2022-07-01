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

"""Plot benchmark curves of fusion algorithm."""

import copy
import matplotlib.pyplot as plt
from pre_process_ai_algo.algo_lib.fusion import Fusion
import time
from typing import Dict

# FPS = 10 interval = 100 ms

ctx_frames = {
    "ab00000de": [
        {
            "guid": "ab00000de",
            "source": 3,
            "ptcId": 1,
            "width": 1.8,
            "length": 3.8,
            "secMark": 59060,
            "timeStamp": 59060,
            "ptcType": "motor",
            "x": 90.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "source": 3,
            "ptcId": 1,
            "secMark": 59110,
            "timeStamp": 59110,
            "ptcType": "motor",
            "x": 91,
            "y": 100,
            "width": 1.8,
            "length": 3.8,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "source": 3,
            "ptcId": 1,
            "secMark": 59160,
            "timeStamp": 59160,
            "ptcType": "motor",
            "width": 1.8,
            "length": 3.8,
            "x": 91.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "source": 3,
            "ptcId": 1,
            "secMark": 59210,
            "timeStamp": 59210,
            "ptcType": "motor",
            "width": 1.8,
            "length": 3.8,
            "x": 92,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "source": 3,
            "ptcId": 1,
            "secMark": 59260,
            "timeStamp": 59260,
            "width": 1.8,
            "length": 3.8,
            "ptcType": "motor",
            "x": 92.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "source": 3,
            "ptcId": 1,
            "secMark": 59310,
            "timeStamp": 59310,
            "ptcType": "motor",
            "x": 93,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "source": 3,
            "ptcId": 1,
            "secMark": 59360,
            "timeStamp": 59360,
            "ptcType": "motor",
            "x": 93.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "source": 3,
            "ptcId": 1,
            "secMark": 59410,
            "timeStamp": 59410,
            "ptcType": "motor",
            "x": 94,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "source": 3,
            "ptcId": 1,
            "secMark": 59460,
            "timeStamp": 59460,
            "ptcType": "motor",
            "x": 94.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "source": 3,
            "ptcId": 1,
            "secMark": 59510,
            "timeStamp": 59510,
            "ptcType": "motor",
            "x": 95,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "source": 3,
            "ptcId": 1,
            "secMark": 59560,
            "timeStamp": 59560,
            "ptcType": "motor",
            "x": 95.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59610,
            "timeStamp": 59610,
            "source": 3,
            "ptcId": 1,
            "ptcType": "motor",
            "x": 96,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59660,
            "timeStamp": 59660,
            "source": 3,
            "ptcId": 1,
            "ptcType": "motor",
            "x": 96.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "source": 3,
            "ptcId": 1,
            "secMark": 59710,
            "timeStamp": 59710,
            "ptcType": "motor",
            "x": 97,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59760,
            "timeStamp": 59760,
            "source": 3,
            "ptcId": 1,
            "ptcType": "motor",
            "x": 97.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59810,
            "timeStamp": 59810,
            "ptcId": 1,
            "source": 3,
            "ptcType": "motor",
            "x": 98,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "source": 3,
            "ptcId": 1,
            "secMark": 59860,
            "timeStamp": 59860,
            "ptcType": "motor",
            "x": 98.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59910,
            "timeStamp": 59910,
            "ptcId": 1,
            "source": 3,
            "ptcType": "motor",
            "x": 99,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
        {
            "guid": "ab00000de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59960,
            "timeStamp": 59960,
            "ptcId": 1,
            "source": 3,
            "ptcType": "motor",
            "x": 99.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
        },
    ],
    "ab00001de": [
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59060,
            "timeStamp": 59060,
            "ptcId": 12,
            "source": 4,
            "ptcType": "motor",
            "x": 90,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59110,
            "timeStamp": 59110,
            "ptcId": 12,
            "source": 4,
            "ptcType": "motor",
            "x": 90.5,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59160,
            "timeStamp": 59160,
            "source": 4,
            "ptcId": 12,
            "ptcType": "motor",
            "x": 91,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "ptcId": 12,
            "secMark": 59210,
            "timeStamp": 59210,
            "source": 4,
            "ptcType": "motor",
            "x": 91.5,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59260,
            "timeStamp": 59260,
            "ptcId": 12,
            "source": 4,
            "ptcType": "motor",
            "x": 92,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59310,
            "timeStamp": 59310,
            "ptcId": 12,
            "source": 4,
            "ptcType": "motor",
            "x": 92.5,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "ptcId": 12,
            "secMark": 59360,
            "timeStamp": 59360,
            "source": 4,
            "ptcType": "motor",
            "x": 93,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "ptcId": 12,
            "secMark": 59410,
            "timeStamp": 59410,
            "source": 4,
            "ptcType": "motor",
            "x": 93.5,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "ptcId": 12,
            "secMark": 59460,
            "timeStamp": 59460,
            "source": 4,
            "ptcType": "motor",
            "x": 94,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "ptcId": 12,
            "secMark": 59510,
            "timeStamp": 59510,
            "source": 4,
            "ptcType": "motor",
            "x": 94.5,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "ptcId": 12,
            "width": 1.8,
            "length": 3.8,
            "secMark": 59560,
            "timeStamp": 59560,
            "source": 4,
            "ptcType": "motor",
            "x": 95,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "ptcId": 12,
            "secMark": 59610,
            "timeStamp": 59610,
            "source": 4,
            "ptcType": "motor",
            "x": 95.5,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "ptcId": 12,
            "secMark": 59660,
            "timeStamp": 59660,
            "source": 4,
            "ptcType": "motor",
            "x": 96,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "ptcId": 12,
            "secMark": 59710,
            "timeStamp": 59710,
            "source": 4,
            "ptcType": "motor",
            "x": 96.5,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "ptcId": 12,
            "secMark": 59760,
            "timeStamp": 59760,
            "source": 4,
            "ptcType": "motor",
            "x": 97,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "ptcId": 12,
            "secMark": 59810,
            "timeStamp": 59810,
            "source": 4,
            "ptcType": "motor",
            "x": 97.5,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "source": 4,
            "ptcId": 12,
            "secMark": 59860,
            "timeStamp": 59860,
            "ptcType": "motor",
            "x": 98,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59910,
            "timeStamp": 59910,
            "ptcId": 12,
            "source": 4,
            "ptcType": "motor",
            "x": 98.5,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
        {
            "guid": "ab00001de",
            "width": 1.8,
            "length": 3.8,
            "secMark": 59960,
            "timeStamp": 59960,
            "ptcId": 12,
            "source": 4,
            "ptcType": "motor",
            "x": 99,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
        },
    ],
}

crt_frame = {
    "ab00000de": {
        "guid": "ab00000de",
        "width": 1.8,
        "length": 3.8,
        "ptcType": "motor",
        "ptcId": 1,
        "source": 3,
        "secMark": 10,
        "x": 100,
        "y": 100,
        "speed": 500,
        "heading": 7200,
    },
    "ab00001de": {
        "guid": "ab00001de",
        "width": 1.8,
        "length": 3.8,
        "secMark": 10,
        "ptcId": 12,
        "source": 4,
        "ptcType": "motor",
        "x": 99.5,
        "y": 100,
        "speed": 1000,
        "heading": 7200,
    },
}

last_ts = 59960


def expand_data(origin_data):
    """Expand data based on original data."""
    new_guid_number = len(origin_data)
    copied_guid_number = new_guid_number - 2
    new_guid = "ab" + str(new_guid_number).zfill(5) + "de"
    copied_guid = "ab" + str(copied_guid_number).zfill(5) + "de"
    new_obj_info = [i for i in origin_data[copied_guid]]
    origin_data[new_guid] = new_obj_info
    for i in new_obj_info:
        i["x"] += 100
        i["y"] += 100
    return origin_data


def expand_current_data(origin_data):
    """Expand data based on original data."""
    new_guid_number = len(origin_data)
    copied_guid_number = new_guid_number - 2
    new_guid = "ab" + str(new_guid_number).zfill(5) + "de"
    copied_guid = "ab" + str(copied_guid_number).zfill(5) + "de"
    new_obj_info = copy.deepcopy(origin_data[copied_guid])

    new_obj_info["x"] += 100
    new_obj_info["y"] += 100
    new_obj_info["global_track_id"] = new_guid
    origin_data[new_guid] = new_obj_info
    return origin_data


def calc_fusion_eff_fps(
    context_frames, current_frame, last_timestamp, matchPairs
):
    """Count times algorithm can run in specific interval."""
    begin_time = time.monotonic_ns()
    count_process_times = 0
    sexp = Fusion()
    while (time.monotonic_ns() - begin_time) / 1000000000 <= process_interval:
        _ = sexp.run(context_frames, current_frame, last_timestamp, matchPairs)
        count_process_times += 1
    return count_process_times


def calc_fusion_eff_time(
    context_frames, current_frame, last_timestamp, matchPairs
):
    """Record the time spent processing a frame of data."""
    begin_time = time.monotonic_ns()
    sexp = Fusion()
    _ = sexp.run(context_frames, current_frame, last_timestamp, matchPairs)
    process_time = time.monotonic_ns() - begin_time
    return process_time / 1000000


def draw_fusion_fps(x, y):
    """Draw the curve of fps result."""
    plt.plot(x, y)
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (times/second)", fontsize=13)
    plt.title("Fusion Algorithm Benchmark", fontsize=15)


def draw_fusion_time(x, y):
    """Draw the curve of time result."""
    plt.plot(x, y)
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (milliseconds/frame)", fontsize=13)
    plt.title("Fusion Algorithm Benchmark", fontsize=15)


max_id_amount = 100
benchmark_point_interval = 10
process_interval = 1  # s

"""fps"""

# matchPairs = {
#       "1.0": ["0.0", "125.0"],
#       "2.0": ["1.0", "124.0"]}
matchPairs: Dict[str, list] = {}  # 若没有前期历史数据就为空。


def draw_benchmark_fps(
    context_frames1, current_frame1, last_timestamp, matchPairs
):
    """Drawing fps curve."""
    benchmark_point_x = []
    benchmark_point_y = []
    while len(context_frames1) < max_id_amount:
        expand_data(context_frames1)
        expand_current_data(current_frame1)
        if len(context_frames1) % benchmark_point_interval == 0:
            benchmark_point_x.append(len(context_frames1))
            benchmark_point_y.append(
                calc_fusion_eff_fps(
                    context_frames1, current_frame1, last_timestamp, matchPairs
                )
            )
    plt.figure(figsize=(8, 5))
    draw_fusion_fps(benchmark_point_x, benchmark_point_y)
    plt.savefig("fusion_algo_benchmark_fps.png", dpi=300)
    plt.savefig("fusion_algo_benchmark_fps.svg")
    plt.show()


ctx_frames1 = copy.deepcopy(ctx_frames)
crt_frame1 = copy.deepcopy(crt_frame)
draw_benchmark_fps(ctx_frames1, crt_frame1, last_ts, matchPairs)

"""time"""


# matchPairs = {
#       "1.0": ["0.0", "125.0"],
#       "2.0": ["1.0", "124.0"]}
# matchPairs: Dict[str, list] = {}  # 若没有前期历史数据就为空。


def draw_benchmark_time(
    context_frames2, current_frame2, last_timestamp, matchPairs
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
                calc_fusion_eff_time(
                    context_frames2, current_frame2, last_timestamp, matchPairs
                )
            )
    plt.figure(figsize=(8, 5))
    draw_fusion_time(benchmark_point_x, benchmark_point_y)
    plt.savefig("fusion_algo_benchmark_time.png", dpi=300)
    plt.savefig("fusion_algo_benchmark_time.svg")
    plt.show()


ctx_frames2 = copy.deepcopy(ctx_frames)
crt_frame2 = copy.deepcopy(crt_frame)
draw_benchmark_time(ctx_frames2, crt_frame2, last_ts, matchPairs)
