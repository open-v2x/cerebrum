"""Plot benchmark curves of smooth algorithm."""

import copy
import matplotlib.pyplot as plt
from pre_process_ai_algo.algo_lib import smooth
import time

# FPS = 10 interval = 100 ms
context_frames = {
    'ab00000de': [
        {'global_track_id': 'ab00000de', 'x': 20, 'y': 60, 'secMark': 59100,
         'timeStamp': 59100},
        {'global_track_id': 'ab00000de', 'x': 30, 'y': 65, 'secMark': 59200,
         'timeStamp': 59200},
        {'global_track_id': 'ab00000de', 'x': 40, 'y': 70, 'secMark': 59300,
         'timeStamp': 59300},
        {'global_track_id': 'ab00000de', 'x': 50, 'y': 75, 'secMark': 59400,
         'timeStamp': 59400},
        {'global_track_id': 'ab00000de', 'x': 60, 'y': 80, 'secMark': 59500,
         'timeStamp': 59500},
        {'global_track_id': 'ab00000de', 'x': 70, 'y': 85, 'secMark': 59600,
         'timeStamp': 59600},
        {'global_track_id': 'ab00000de', 'x': 80, 'y': 90, 'secMark': 59700,
         'timeStamp': 59700},
        {'global_track_id': 'ab00000de', 'x': 90, 'y': 95, 'secMark': 59800,
         'timeStamp': 59800},
        {'global_track_id': 'ab00000de', 'x': 100, 'y': 100, 'secMark': 59900,
         'timeStamp': 59900}],
    'ab00001de': [
        {'global_track_id': 'ab00001de', 'x': 20, 'y': 60, 'secMark': 59100,
         'timeStamp': 59100},
        {'global_track_id': 'ab00001de', 'x': 30, 'y': 65, 'secMark': 59200,
         'timeStamp': 59200},
        {'global_track_id': 'ab00001de', 'x': 40, 'y': 70, 'secMark': 59300,
         'timeStamp': 59300},
        {'global_track_id': 'ab00001de', 'x': 50, 'y': 75, 'secMark': 59400,
         'timeStamp': 59400},
        {'global_track_id': 'ab00001de', 'x': 60, 'y': 80, 'secMark': 59500,
         'timeStamp': 59500},
        {'global_track_id': 'ab00001de', 'x': 70, 'y': 85, 'secMark': 59600,
         'timeStamp': 59600},
        {'global_track_id': 'ab00001de', 'x': 80, 'y': 90, 'secMark': 59700,
         'timeStamp': 59700},
        {'global_track_id': 'ab00001de', 'x': 90, 'y': 95, 'secMark': 59800,
         'timeStamp': 59800},
        {'global_track_id': 'ab00001de', 'x': 100, 'y': 100, 'secMark': 59900,
         'timeStamp': 59900}]
}
current_frame = {
    'ab00000de':
        {'global_track_id': 'ab00000de', 'x': 130, 'y': 110, 'secMark': 100,
         'timeStamp': 100},
    'ab00001de':
        {'global_track_id': 'ab00001de', 'x': 130, 'y': 110, 'secMark': 100,
         'timeStamp': 100}}
last_ts = 59900


def expand_data(origin_data):
    """Expand data based on original data."""
    new_guid_number = len(origin_data)
    copied_guid_number = new_guid_number - 2
    new_guid = "ab" + str(new_guid_number).zfill(5) + "de"
    copied_guid = "ab" + str(copied_guid_number).zfill(5) + "de"
    new_obj_info = copy.deepcopy(origin_data[copied_guid])
    # new_obj_info = [i for i in origin_data[copied_guid]]
    origin_data[new_guid] = new_obj_info
    for i in new_obj_info:
        i['x'] += 100
        i['y'] += 100
        i['global_track_id'] = new_guid
    return origin_data


def expand_current_data(origin_data):
    """Expand data based on original data."""
    new_guid_number = len(origin_data)
    copied_guid_number = new_guid_number - 2
    new_guid = "ab" + str(new_guid_number).zfill(5) + "de"
    copied_guid = "ab" + str(copied_guid_number).zfill(5) + "de"
    new_obj_info = copy.deepcopy(origin_data[copied_guid])
    # new_obj_info = [i for i in origin_data[copied_guid]]
    new_obj_info['x'] += 100
    new_obj_info['y'] += 100
    new_obj_info['global_track_id'] = new_guid
    # new_obj_info = [i for i in origin_data[copied_guid]]
    origin_data[new_guid] = new_obj_info
    return origin_data


def calc_expsmooth_eff_fps(context_frames, current_frame, last_timestamp):
    """Count times algorithm can run in specific interval."""
    begin_time = time.time()
    count_process_times = 0
    sexp = smooth.Exponential()
    while time.time() - begin_time <= process_interval:
        context_frames_new = copy.deepcopy(context_frames)
        current_frame_new = copy.deepcopy(current_frame)
        last_timestamp_new = copy.deepcopy(last_timestamp)
        _ = sexp.run(context_frames_new, current_frame_new, last_timestamp_new)
        count_process_times += 1
    return count_process_times


def calc_polysmooth_eff_fps(context_frames, current_frame, last_timestamp):
    """Count times algorithm can run in specific interval."""
    begin_time = time.time()
    count_process_times = 0
    spoly = smooth.Polynomial()
    while time.time() - begin_time <= process_interval:
        context_frames_new = copy.deepcopy(context_frames)
        current_frame_new = copy.deepcopy(current_frame)
        last_timestamp_new = copy.deepcopy(last_timestamp)
        _ = spoly.run(context_frames_new, current_frame_new,
                      last_timestamp_new)
        count_process_times += 1
    return count_process_times


def calc_expsmooth_eff_time(context_frames, current_frame, last_timestamp):
    """Record the time spent processing a frame of data."""
    begin_time = time.time()
    sexp = smooth.Exponential()
    context_frames_new = copy.deepcopy(context_frames)
    current_frame_new = copy.deepcopy(current_frame)
    last_timestamp_new = copy.deepcopy(last_timestamp)
    _ = sexp.run(context_frames_new, current_frame_new, last_timestamp_new)
    process_time = time.time() - begin_time
    return process_time * 1000


def calc_polysmooth_eff_time(context_frames, current_frame, last_timestamp):
    """Record the time spent processing a frame of data."""
    begin_time = time.time()
    spoly = smooth.Polynomial()
    context_frames_new = copy.deepcopy(context_frames)
    current_frame_new = copy.deepcopy(current_frame)
    last_timestamp_new = copy.deepcopy(last_timestamp)
    _ = spoly.run(context_frames_new, current_frame_new, last_timestamp_new)
    process_time = time.time() - begin_time
    return process_time * 1000


def draw_expsmooth_fps(x, y):
    """Draw the curve of fps result."""
    plt.plot(x, y, color="red", label="Exponential smooth")
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (times/second)", fontsize=13)


def draw_polysmooth_fps(x, y):
    """Draw the curve of fps result."""
    plt.plot(x, y, color="blue", label="Polynomial smooth")
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (times/second)", fontsize=13)


def draw_expsmooth_time(x, y):
    """Draw the curve of time result."""
    plt.plot(x, y, color="red", label="Exponential smooth")
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (milliseconds/frame)", fontsize=13)


def draw_polysmooth_time(x, y):
    """Draw the curve of time result."""
    plt.plot(x, y, color="blue", label="Polynomial smooth")
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (milliseconds/frame)", fontsize=13)


max_id_amount = 500
benchmark_point_interval = 20
process_interval = 1  # s


def draw_benchmark_fps(context_frames1, current_frame1, last_timestamp):
    """Drawing fps curve."""
    data1 = copy.deepcopy(context_frames1)
    data2 = copy.deepcopy(current_frame1)
    data3 = copy.deepcopy(last_timestamp)
    benchmark_point_x = []
    benchmark_point_y1 = []
    benchmark_point_y2 = []
    while len(context_frames1) < max_id_amount:
        expand_data(context_frames1)
        expand_current_data(current_frame1)
        if len(context_frames1) % benchmark_point_interval == 0:
            benchmark_point_x.append(len(context_frames1))
            benchmark_point_y1.append(
                calc_expsmooth_eff_fps(context_frames1, current_frame1,
                                       last_timestamp))
            benchmark_point_y2.append(
                calc_polysmooth_eff_fps(data1, data2, data3))
    plt.figure(figsize=(8, 5))
    draw_expsmooth_fps(benchmark_point_x, benchmark_point_y1)
    draw_polysmooth_fps(benchmark_point_x, benchmark_point_y2)
    plt.title('Smooth Algorithm Benchmark', fontsize=15)
    plt.legend()
    plt.show()
    plt.savefig('Smooth_algo_benchmark_fps_' + str(max_id_amount) + '.png',
                dpi=300)
    plt.savefig('Smooth_algo_benchmark_fps_' + str(max_id_amount) + '.svg')


ctx_frames1 = copy.deepcopy(context_frames)
crt_frame1 = copy.deepcopy(current_frame)
# origin_radar_data1 = copy.deepcopy(context_frames)
draw_benchmark_fps(ctx_frames1, crt_frame1, last_ts)


def draw_benchmark_time(context_frames2, current_frame2, last_timestamp):
    """Drawing time curve."""
    data1 = copy.deepcopy(context_frames2)
    data2 = copy.deepcopy(current_frame2)
    data3 = copy.deepcopy(last_timestamp)
    benchmark_point_x = []
    benchmark_point_y1 = []
    benchmark_point_y2 = []
    while len(context_frames2) < max_id_amount:
        expand_data(context_frames2)
        expand_current_data(current_frame2)
        if len(context_frames2) % benchmark_point_interval == 0:
            benchmark_point_x.append(len(context_frames2))
            benchmark_point_y1.append(
                calc_expsmooth_eff_time(context_frames2, current_frame2,
                                        last_timestamp))
            benchmark_point_y2.append(
                calc_polysmooth_eff_time(data1, data2, data3))
    plt.figure(figsize=(8, 5))
    draw_expsmooth_time(benchmark_point_x, benchmark_point_y1)
    draw_polysmooth_time(benchmark_point_x, benchmark_point_y2)
    plt.title('Smooth Algorithm Benchmark', fontsize=15)
    plt.legend()
    plt.show()
    plt.savefig('Smooth_algo_benchmark_time_' + str(max_id_amount) + '.png',
                dpi=300)
    plt.savefig('Smooth_algo_benchmark_time_' + str(max_id_amount) + '.svg')


ctx_frames2 = copy.deepcopy(context_frames)
crt_frame2 = copy.deepcopy(current_frame)
draw_benchmark_time(ctx_frames2, crt_frame2, last_ts)
