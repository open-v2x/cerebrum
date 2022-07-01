"""Plot benchmark curves of complement algorithm."""

import copy
import matplotlib.pyplot as plt
from pre_process_ai_algo.algo_lib import complement
import time

# FPS = 10 interval = 100 ms
ctx_frames = {
    'ab00000de': [
        {'global_track_id': 'ab00000de',
         'secMark': 59300,
         'timeStamp': 59300,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00000de',
         'secMark': 59400,
         'timeStamp': 59400,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00000de',
         'secMark': 59500,
         'timeStamp': 59500,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00000de',
         'secMark': 59600,
         'timeStamp': 59600,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00000de',
         'secMark': 59700,
         'timeStamp': 59700,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00000de',
         'secMark': 59800,
         'timeStamp': 59800,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00000de',
         'secMark': 59900,
         'timeStamp': 59900,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00000de',
         'secMark': 100,
         'timeStamp': 100,
         'ptcType': 'motor',
         'x': 98.5,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00000de',
         'secMark': 300,
         'timeStamp': 300,
         'ptcType': 'motor',
         'x': 99.5,
         'y': 100,
         'speed': 500,
         'heading': 7200
         }
    ],
    'ab00001de': [
        {'global_track_id': 'ab00001de',
         'secMark': 59300,
         'timeStamp': 59300,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00001de',
         'secMark': 59400,
         'timeStamp': 59400,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00001de',
         'secMark': 59500,
         'timeStamp': 59500,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00001de',
         'secMark': 59600,
         'timeStamp': 59600,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00001de',
         'secMark': 59700,
         'timeStamp': 59700,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00001de',
         'secMark': 59800,
         'timeStamp': 59800,
         'ptcType': 'motor',
         'x': 98,
         'y': 100,
         'speed': 500,
         'heading': 7200
         },
        {'global_track_id': 'ab00001de',
         'secMark': 59900,
         'timeStamp': 59900,
         'ptcType': 'motor',
         'x': 46,
         'y': 100,
         'speed': 1000,
         'heading': 7200
         },
        {'global_track_id': 'ab00001de',
         'secMark': 100,
         'timeStamp': 100,
         'ptcType': 'motor',
         'x': 56,
         'y': 100,
         'speed': 1000,
         'heading': 7200
         },
        {'global_track_id': 'ab00001de',
         'secMark': 300,
         'timeStamp': 300,
         'ptcType': 'motor',
         'x': 77,
         'y': 100,
         'speed': 1000,
         'heading': 7200
         }
    ],
}

crt_frame = {
    'ab00000de':
        {'global_track_id': 'ab00000de',
         'ptcType': 'motor',
         'secMark': 400,
         'timeStamp': 400,
         'x': 100,
         'y': 100,
         'speed': 500,
         'heading': 7200
         }
    ,
    'ab00001de':
        {'global_track_id': 'ab00001de',
         'secMark': 400,
         'timeStamp': 400,
         'ptcType': 'motor',
         'x': 88,
         'y': 100,
         'speed': 1000,
         'heading': 7200
         }
}
last_ts = 300


def expand_data(origin_data):
    """Expand data based on original data."""
    new_guid_number = len(origin_data)
    copied_guid_number = new_guid_number - 2
    new_guid = "ab" + str(new_guid_number).zfill(5) + "de"
    copied_guid = "ab" + str(copied_guid_number).zfill(5) + "de"
    new_obj_info = copy.deepcopy(origin_data[copied_guid])
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

    new_obj_info['x'] += 100
    new_obj_info['y'] += 100
    new_obj_info['global_track_id'] = new_guid
    # print(new_obj_info)
    origin_data[new_guid] = new_obj_info
    return origin_data


def calc_interp_eff_fps(context_frames, current_frame, last_timestamp):
    """Count times algorithm can run in specific interval."""
    begin_time = time.time()
    count_process_times = 0
    sexp = complement.Interpolation()
    while time.time() - begin_time <= process_interval:
        context_frames_new = copy.deepcopy(context_frames)
        current_frame_new = copy.deepcopy(current_frame)
        last_timestamp_new = copy.deepcopy(last_timestamp)
        _ = sexp.run(context_frames_new, current_frame_new, last_timestamp_new)
        count_process_times += 1
    return count_process_times


def calc_interp_eff_time(context_frames, current_frame, last_timestamp):
    """Record the time spent processing a frame of data."""
    begin_time = time.time()
    sexp = complement.Interpolation()
    context_frames_new = copy.deepcopy(context_frames)
    current_frame_new = copy.deepcopy(current_frame)
    last_timestamp_new = copy.deepcopy(last_timestamp)
    _ = sexp.run(context_frames_new, current_frame_new, last_timestamp_new)
    process_time = time.time() - begin_time
    return process_time * 1000


def draw_interp_fps(x, y):
    """Draw the curve of fps result."""
    plt.plot(x, y, color="red", label='Interpolation')
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (times/second)", fontsize=13)


def draw_interp_time(x, y):
    """Draw the curve of time result."""
    plt.plot(x, y, color="red", label='Interpolation')
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (milliseconds/frame)", fontsize=13)


def calc_lstm_eff_fps(context_frames, current_frame, last_timestamp):
    """Count times algorithm can run in specific interval."""
    begin_time = time.time()
    count_process_times = 0
    sexp = complement.LstmPredict()
    while time.time() - begin_time <= process_interval:
        context_frames_new = copy.deepcopy(context_frames)
        current_frame_new = copy.deepcopy(current_frame)
        last_timestamp_new = copy.deepcopy(last_timestamp)
        _ = sexp.run(context_frames_new, current_frame_new, last_timestamp_new)
        count_process_times += 1
    return count_process_times


def calc_lstm_eff_time(context_frames, current_frame, last_timestamp):
    """Record the time spent processing a frame of data."""
    begin_time = time.time()
    sexp = complement.LstmPredict()
    context_frames_new = copy.deepcopy(context_frames)
    current_frame_new = copy.deepcopy(current_frame)
    last_timestamp_new = copy.deepcopy(last_timestamp)
    _ = sexp.run(context_frames_new, current_frame_new, last_timestamp_new)
    process_time = time.time() - begin_time
    return process_time * 1000


def draw_lstm_fps(x, y):
    """Draw the curve of fps result."""
    plt.plot(x, y, color="blue", label='LSTM')
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (times/second)", fontsize=13)


def draw_lstm_time(x, y):
    """Draw the curve of time result."""
    plt.plot(x, y, color="blue", label='LSTM')
    plt.xlabel("data amount (traffic participants/frame)", fontsize=13)
    plt.ylabel("algorithmic efficiency (milliseconds/frame)", fontsize=13)


max_id_amount = 500
benchmark_point_interval = 50
process_interval = 1  # s

"""fps"""


def draw_benchmark_fps(ctx_frames1, crt_frame1, last_timestamp):
    """Drawing fps curve."""
    data1 = copy.deepcopy(ctx_frames1)
    data2 = copy.deepcopy(crt_frame1)
    data3 = copy.deepcopy(last_timestamp)
    benchmark_point_x = []
    benchmark_point_y1 = []
    benchmark_point_y2 = []
    while len(ctx_frames1) < max_id_amount:
        expand_data(ctx_frames1)
        expand_current_data(crt_frame1)
        if len(ctx_frames1) % benchmark_point_interval == 0:
            # print(ctx_frames1)
            benchmark_point_x.append(len(ctx_frames1))
            benchmark_point_y1.append(
                calc_interp_eff_fps(ctx_frames1, crt_frame1, last_timestamp))
            benchmark_point_y2.append(calc_lstm_eff_fps(data1, data2, data3))
    plt.figure(figsize=(8, 5))
    plt.title('Complement Algorithm Benchmark', fontsize=15)
    draw_interp_time(benchmark_point_x, benchmark_point_y1)
    draw_lstm_time(benchmark_point_x, benchmark_point_y2)
    plt.legend()
    plt.show()


ctx_frames1 = copy.deepcopy(ctx_frames)
crt_frame1 = copy.deepcopy(crt_frame)
draw_benchmark_fps(ctx_frames1, crt_frame1, last_ts)
plt.savefig('Complement_algo_benchmark_fps_' + str(max_id_amount) + '.png',
            dpi=300)
plt.savefig('Complement_algo_benchmark_fps_' + str(max_id_amount) + '.svg')

"""time"""


def draw_benchmark_time(context_frames2, current_frame2, last_timestamp):
    """Drawing time curve."""
    data1 = copy.deepcopy(ctx_frames1)
    data2 = copy.deepcopy(crt_frame1)
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
                calc_interp_eff_time(context_frames2, current_frame2,
                                     last_timestamp))
            benchmark_point_y2.append(calc_lstm_eff_time(data1, data2, data3))
    plt.figure(figsize=(8, 5))
    plt.title('Complement Algorithm Benchmark', fontsize=15)
    draw_interp_time(benchmark_point_x, benchmark_point_y1)
    draw_lstm_time(benchmark_point_x, benchmark_point_y2)
    plt.legend()
    plt.show()


context_frames2 = copy.deepcopy(ctx_frames)
current_frame2 = copy.deepcopy(crt_frame)
draw_benchmark_time(context_frames2, current_frame2, last_ts)
plt.savefig('Complement_algo_benchmark_time_' + str(max_id_amount) + '.png',
            dpi=300)
plt.savefig('Complement_algo_benchmark_time_' + str(max_id_amount) + '.svg')
