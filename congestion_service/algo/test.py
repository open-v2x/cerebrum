with open("test_data.txt", "r") as f:
    context_frames = eval(f.readline())

    latest_frame = eval(f.readline())

last_ts = 45400
msg = [
    {
        "secMark": 45400,
        "congestionLanesInfo": {
            "laneId": 14,
            "level": 3,
            "avgSpeed": 1,
            "startPoint": {"lat": 319353462, "lon": 1188214495},
            "endPoint": {"lat": 319352922, "lon": 1188219175},
        },
    },
    {
        "secMark": 45400,
        "congestionLanesInfo": {
            "laneId": 15,
            "level": 3,
            "avgSpeed": 1,
            "startPoint": {"lat": 319353218, "lon": 1188214143},
            "endPoint": {"lat": 319352678, "lon": 1188218913},
        },
    },
    {
        "secMark": 45400,
        "congestionLanesInfo": {
            "laneId": 20,
            "level": 0,
            "avgSpeed": 121,
            "startPoint": {"lat": 319350758, "lon": 1188222844},
            "endPoint": {"lat": 319350758, "lon": 1188222844},
        },
    },
    {
        "secMark": 45400,
        "congestionLanesInfo": {
            "laneId": 21,
            "level": 0,
            "avgSpeed": 121,
            "startPoint": {"lat": 319350728, "lon": 1188223163},
            "endPoint": {"lat": 319350728, "lon": 1188223163},
        },
    },
]
show_info = [
    {
        "type": "CGW",
        "level": 3,
        "startPoint": {"x": 6.639107501303577, "y": 56.342885352479925},
        "endPoint": {"x": 50.832657436020185, "y": 49.87286125184782},
    },
    {
        "type": "CGW",
        "level": 3,
        "startPoint": {"x": 3.280832450455666, "y": 53.67497677013696},
        "endPoint": {"x": 48.325521790833946, "y": 47.19567986911201},
    },
    {
        "type": "CGW",
        "level": 0,
        "startPoint": {"x": 85.22208619107394, "y": 26.4892169662188},
        "endPoint": {"x": 85.22208619107394, "y": 26.4892169662188},
    },
    {
        "type": "CGW",
        "level": 0,
        "startPoint": {"x": 88.2355688838384, "y": 26.123624461659467},
        "endPoint": {"x": 88.2355688838384, "y": 26.123624461659467},
    },
]

# last_ts = 45400

CG_KEY = "cg.R328328"
rsu = "R328328"
min_con_range = [25, 30]
mid_con_range = [15, 24]
max_con_range = [0, 14]
lane_info = {
    "14": -1,
    "15": -1,
    "20": -1,
    "21": -1,
    "22": -1,
    "16": 1,
    "17": 1,
    "18": 1,
    "19": 1,
    "23": 1,
    "24": 1,
    "1": 1,
    "4": 1,
    "5": 1,
    "6": 1,
    "7": 1,
    "11": 1,
    "12": 1,
    "13": 1,
    "8": -1,
    "9": -1,
    "10": -1,
    "2": -1,
    "3": -1,
}


def http_test():
    import requests

    response = requests.post(
        url="http://127.0.0.1:28304/congestion",
        json={
            "context_frames": context_frames,
            "current_frame": latest_frame,
            "last_timestamp": last_ts,
            "rsu": rsu,
            "min_con_range": min_con_range,
            "mid_con_range": mid_con_range,
            "max_con_range": max_con_range,
            "lane_info": lane_info,
        },
    )

    res = response.json()
    print(res.get("msg") == msg)
    # print(res.get("msg"))
    print(res.get("info") == show_info)
    print(res.get("last_timestamp") == last_ts)
    print(res.get("cg_key") == CG_KEY)


def grpc_test():
    import grpc
    from congestion_service.grpc_server import (
        congestion_grpc_pb2_grpc,
        congestion_grpc_pb2,
    )
    import json

    with grpc.insecure_channel("127.0.0.1:28305") as channel:
        stub = congestion_grpc_pb2_grpc.CongestionGrpcStub(channel)
        data = congestion_grpc_pb2.CongestionRequest(
            data=json.dumps(
                {
                    "context_frames": context_frames,
                    "current_frame": latest_frame,
                    "last_timestamp": last_ts,
                    "rsu": rsu,
                    "min_con_range": min_con_range,
                    "mid_con_range": mid_con_range,
                    "max_con_range": max_con_range,
                    "lane_info": lane_info,
                }
            )
        )
        response = stub.congestion(data)
        res = json.loads(response.data)
        print(res.get("msg") == msg)
        # print(res.get("msg"))
        print(res.get("info") == show_info)
        print(res.get("last_timestamp") == last_ts)
        print(res.get("cg_key") == CG_KEY)


#
async def ws_test():
    from websockets.client import connect
    import json

    async with connect(
        "ws://127.0.0.1:28304/ws",
    ) as websocket:
        await websocket.send(
            json.dumps(
                {
                    "context_frames": context_frames,
                    "current_frame": latest_frame,
                    "last_timestamp": last_ts,
                    "rsu": rsu,
                    "min_con_range": min_con_range,
                    "mid_con_range": mid_con_range,
                    "max_con_range": max_con_range,
                    "lane_info": lane_info,
                }
            )
        )
        data = await websocket.recv()
        res = json.loads(data)
        print(res.get("msg") == msg)
        # print(res.get("msg"))
        print(res.get("info") == show_info)
        print(res.get("last_timestamp") == last_ts)
        print(res.get("cg_key") == CG_KEY)


if __name__ == "__main__":
    # import asyncio
    #
    # http_test()
    # grpc_test()
    # asyncio.run(ws_test())
    from algo_lib import CongestionWarning

    warning = CongestionWarning()
    msg_, show_info_, last_timestamp, CG_KEY_ = warning.run(
        context_frames=context_frames,
        current_frame=latest_frame,
        last_timestamp=last_ts,
        rsu=rsu,
        min_con_range=min_con_range,
        mid_con_range=mid_con_range,
        max_con_range=max_con_range,
        lane_info=lane_info,
        )

    print(msg_ == msg)
    print(show_info_ == show_info)
    print(last_timestamp == last_ts)
    print(CG_KEY_ == CG_KEY)
