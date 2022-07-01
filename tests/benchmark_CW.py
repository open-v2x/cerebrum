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

"""Plot benchmark curves of collision warning algorithm."""

import copy
import matplotlib.pyplot as plt
from scenario_algo.algo_lib import collision_warning
import time

# FPS = 10 interval = 100 ms
ctx_frames = {
    "ab00000de": [
        {
            "global_track_id": "ab00000de",
            "secMark": 59560,
            "timeStamp": 59560,
            "ptcType": "motor",
            "x": 95.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00000de",
            "secMark": 59610,
            "timeStamp": 59610,
            "ptcType": "motor",
            "x": 96,
            "y": 100,
            "speed": 500,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00000de",
            "secMark": 59660,
            "timeStamp": 59660,
            "ptcType": "motor",
            "x": 96.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00000de",
            "secMark": 59710,
            "timeStamp": 59710,
            "ptcType": "motor",
            "x": 97,
            "y": 100,
            "speed": 500,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00000de",
            "secMark": 59760,
            "timeStamp": 59760,
            "ptcType": "motor",
            "x": 97.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00000de",
            "secMark": 59810,
            "timeStamp": 59810,
            "ptcType": "motor",
            "x": 98,
            "y": 100,
            "speed": 500,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00000de",
            "secMark": 59860,
            "timeStamp": 59860,
            "ptcType": "motor",
            "x": 98.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00000de",
            "secMark": 59910,
            "timeStamp": 59910,
            "ptcType": "motor",
            "x": 99,
            "y": 100,
            "speed": 500,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00000de",
            "secMark": 59960,
            "timeStamp": 59960,
            "ptcType": "motor",
            "x": 99.5,
            "y": 100,
            "speed": 500,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
    ],
    "ab00001de": [
        {
            "global_track_id": "ab00001de",
            "secMark": 59560,
            "timeStamp": 59560,
            "ptcType": "motor",
            "x": 81,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00001de",
            "secMark": 59610,
            "timeStamp": 59610,
            "ptcType": "motor",
            "x": 82,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00001de",
            "secMark": 59660,
            "timeStamp": 59660,
            "ptcType": "motor",
            "x": 83,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00001de",
            "secMark": 59710,
            "timeStamp": 59710,
            "ptcType": "motor",
            "x": 84,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00001de",
            "secMark": 59760,
            "timeStamp": 59760,
            "ptcType": "motor",
            "x": 85,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00001de",
            "secMark": 59810,
            "timeStamp": 59810,
            "ptcType": "motor",
            "x": 86,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00001de",
            "secMark": 59860,
            "timeStamp": 59860,
            "ptcType": "motor",
            "x": 87,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00001de",
            "secMark": 59910,
            "timeStamp": 59910,
            "ptcType": "motor",
            "x": 88,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00001de",
            "secMark": 59960,
            "timeStamp": 59960,
            "ptcType": "motor",
            "x": 89,
            "y": 100,
            "speed": 1000,
            "heading": 7200,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
    ],
    "ab00002de": [
        {
            "global_track_id": "ab00002de",
            "secMark": 59560,
            "timeStamp": 59560,
            "ptcType": "motor",
            "x": 200,
            "y": 293,
            "speed": 1000,
            "heading": 0,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00002de",
            "secMark": 59610,
            "timeStamp": 59610,
            "ptcType": "motor",
            "x": 200,
            "y": 294,
            "speed": 1000,
            "heading": 0,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00002de",
            "secMark": 59660,
            "timeStamp": 59660,
            "ptcType": "motor",
            "x": 200,
            "y": 295,
            "speed": 1000,
            "heading": 0,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00002de",
            "secMark": 59710,
            "timeStamp": 59710,
            "ptcType": "motor",
            "x": 200,
            "y": 296,
            "speed": 1000,
            "heading": 0,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00002de",
            "secMark": 59760,
            "timeStamp": 59760,
            "ptcType": "motor",
            "x": 200,
            "y": 297,
            "speed": 1000,
            "heading": 0,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00002de",
            "secMark": 59810,
            "timeStamp": 59810,
            "ptcType": "motor",
            "x": 200,
            "y": 298,
            "speed": 1000,
            "heading": 0,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00002de",
            "secMark": 59860,
            "timeStamp": 59860,
            "ptcType": "motor",
            "x": 200,
            "y": 299,
            "speed": 1000,
            "heading": 0,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00002de",
            "secMark": 59910,
            "timeStamp": 59910,
            "ptcType": "motor",
            "x": 200,
            "y": 300,
            "speed": 1000,
            "heading": 0,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
        {
            "global_track_id": "ab00002de",
            "secMark": 59960,
            "timeStamp": 59960,
            "ptcType": "motor",
            "x": 200,
            "y": 301,
            "speed": 1000,
            "heading": 0,
            "lat": 31.935221261941393,
            "lon": 118.82304885831456,
        },
    ],
}

crt_frame = {
    "ab00000de": {
        "global_track_id": "ab00000de",
        "ptcType": "motor",
        "secMark": 10,
        "x": 100,
        "y": 100,
        "speed": 500,
        "heading": 7200,
        "lat": 31.935221261941393,
        "lon": 118.82304885831456,
        "ele": 100,
    },
    "ab00001de": {
        "global_track_id": "ab00001de",
        "ptcType": "motor",
        "secMark": 10,
        "x": 90,
        "y": 100,
        "speed": 1000,
        "heading": 7200,
        "lat": 31.935221261941393,
        "lon": 118.82304885831456,
        "ele": 100,
    },
    "ab00002de": {
        "global_track_id": "ab00002de",
        "ptcType": "motor",
        "secMark": 10,
        "x": 200,
        "y": 302,
        "speed": 1000,
        "heading": 0,
        "lat": 31.935221261941393,
        "lon": 118.82304885831456,
        "ele": 100,
    },
}
last_ts = 59960


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


def calc_collision_eff_fps(context_frames, current_frame, last_timestamp):
    """Count times algorithm can run in specific interval."""
    begin_time = time.monotonic_ns()
    count_process_times = 0
    sexp = collision_warning.CollisionWarning()
    while (time.monotonic_ns() - begin_time) / 1000000000 <= process_interval:
        context_frames_new = copy.deepcopy(context_frames)
        current_frame_new = copy.deepcopy(current_frame)
        last_timestamp_new = copy.deepcopy(last_timestamp)
        _ = sexp.run(context_frames_new, current_frame_new, last_timestamp_new)
        count_process_times += 1
    return count_process_times


def calc_collision_eff_time(context_frames, current_frame, last_timestamp):
    """Record the time spent processing a frame of data."""
    begin_time = time.monotonic_ns()
    sexp = collision_warning.CollisionWarning()
    context_frames_new = copy.deepcopy(context_frames)
    current_frame_new = copy.deepcopy(current_frame)
    last_timestamp_new = copy.deepcopy(last_timestamp)
    _ = sexp.run(context_frames_new, current_frame_new, last_timestamp_new)
    process_time = time.monotonic_ns() - begin_time
    return process_time / 1000000


def draw_collision_fps(x, y):
    """Draw the curve of fps result."""
    plt.plot(x, y)
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (times/second)", fontsize=13)
    plt.title("Collision Warning Algorithm Benchmark", fontsize=15)


def draw_collision_time(x, y):
    """Draw the curve of time result."""
    plt.plot(x, y)
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (milliseconds/frame)", fontsize=13)
    plt.title("Collision Warning Algorithm Benchmark", fontsize=15)


max_id_amount = 100
benchmark_point_interval = 5
process_interval = 1  # s

"""fps"""


def draw_benchmark_fps(context_frames1, current_frame1, last_timestamp):
    """Drawing fps curve."""
    benchmark_point_x = []
    benchmark_point_y = []
    while len(context_frames1) < max_id_amount:
        expand_data(context_frames1)
        expand_current_data(current_frame1)
        if len(context_frames1) % benchmark_point_interval == 0:
            benchmark_point_x.append(len(context_frames1))
            benchmark_point_y.append(
                calc_collision_eff_fps(
                    context_frames1, current_frame1, last_timestamp
                )
            )
    plt.figure(figsize=(8, 5))
    draw_collision_fps(benchmark_point_x, benchmark_point_y)
    plt.savefig("collision_algo_benchmark_fps.png", dpi=300)
    plt.savefig("collision_algo_benchmark_fps.svg")
    plt.show()


ctx_frames1 = copy.deepcopy(ctx_frames)
crt_frame1 = copy.deepcopy(crt_frame)
draw_benchmark_fps(ctx_frames1, crt_frame1, last_ts)


"""time"""


def draw_benchmark_time(context_frames2, current_frame2, last_timestamp):
    """Drawing time curve."""
    benchmark_point_x = []
    benchmark_point_y = []
    while len(context_frames2) < max_id_amount:
        expand_data(context_frames2)
        expand_current_data(current_frame2)
        if len(context_frames2) % benchmark_point_interval == 0:
            benchmark_point_x.append(len(context_frames2))
            benchmark_point_y.append(
                calc_collision_eff_time(
                    context_frames2, current_frame2, last_timestamp
                )
            )
    plt.figure(figsize=(8, 5))
    draw_collision_time(benchmark_point_x, benchmark_point_y)
    plt.savefig("collision_algo_benchmark_time.png", dpi=300)
    plt.savefig("collision_algo_benchmark_time.svg")
    plt.show()


ctx_frames2 = copy.deepcopy(ctx_frames)
crt_frame2 = copy.deepcopy(crt_frame)
draw_benchmark_time(ctx_frames2, crt_frame2, last_ts)
