import asyncio

with open("data.txt", "r") as f:
    motor_traj = eval(f.readline())

vptc_traj = {}
rsi = {}
params = {
    "msgCnt": "2",
    "id": "147",
    "refPos": {"lon": 1188222830, "lat": 319351055, "ele": 100},
    "secMark": 45300,
    "timeStamp": 1653016785300,
    "intAndReq": {
        "reqs": {
            "reqID": 2,
            "status": 2,
            "targetRSU": "R328328",
            "reqPriority": "B11100000",
            "info": {
                "sensorSharing": {
                    "detectArea": {
                        "activePath": [
                            {"lon": 1188222830, "lat": 319351055, "ele": 100},
                            {"lon": 1188222844, "lat": 319350758, "ele": 100},
                            {"lon": 1188222858, "lat": 319350461, "ele": 100},
                            {"lon": 1188222873, "lat": 319350164, "ele": 100},
                            {"lon": 1188222888, "lat": 319349867, "ele": 100},
                        ]
                    }
                }
            },
            "lifeTime": 50,
        }
    },
}
convert_info = [40388545, 3535296]
sensor_pos = {"lon": 1188213963, "lat": 319348466}
msg = {
    "msgCnt": 2,
    "id": "R328328",
    "equipmentType": 1,
    "sensorPos": {"lon": 1188213963, "lat": 319348466},
    "secMark": 35545,
    "egoPos": {"lon": 1188222830, "lat": 319351055, "ele": 100},
    "egoId": "147",
    "participants": [
        {
            "ptcType": "motor",
            "ptcHistoricalTrajectory": [
                {"lat": 319348934, "lon": 1188222602},
                {"lat": 319349214, "lon": 1188222587},
                {"lat": 319349526, "lon": 1188222569},
                {"lat": 319349818, "lon": 1188222553},
                {"lat": 319350080, "lon": 1188222537},
                {"lat": 319350308, "lon": 1188222270},
                {"lat": 319350544, "lon": 1188222206},
            ],
            "ptcPredictedTrajectory": [
                {"lat": 319351186, "lon": 1188222012},
                {"lat": 319351772, "lon": 1188221757},
                {"lat": 319352300, "lon": 1188221442},
                {"lat": 319352772, "lon": 1188221068},
                {"lat": 319353187, "lon": 1188220634},
                {"lat": 319353545, "lon": 1188220141},
            ],
            "ptcTrackTimeStamp": 1691119595439,
            "ptcSize": {"width": 180, "length": 500, "height": 30},
            "ptcHeading": 254,
            "ptcAngleSpeed": 0,
        },
        {
            "ptcType": "motor",
            "ptcHistoricalTrajectory": [
                {"lat": 319349005, "lon": 1188222281},
                {"lat": 319349364, "lon": 1188222261},
                {"lat": 319349796, "lon": 1188222236},
                {"lat": 319350241, "lon": 1188222211},
                {"lat": 319350690, "lon": 1188222186},
                {"lat": 319351139, "lon": 1188222159},
                {"lat": 319351588, "lon": 1188222132},
            ],
            "ptcPredictedTrajectory": [
                {"lat": 319352721, "lon": 1188222066},
                {"lat": 319353966, "lon": 1188221991},
                {"lat": 319355323, "lon": 1188221908},
                {"lat": 319356793, "lon": 1188221816},
                {"lat": 319358374, "lon": 1188221715},
                {"lat": 319360068, "lon": 1188221606},
            ],
            "ptcTrackTimeStamp": 1691119595439,
            "ptcSize": {"width": 150, "length": 520, "height": 47},
            "ptcHeading": 254,
            "ptcAngleSpeed": 0,
        },
        {
            "ptcType": "motor",
            "ptcHistoricalTrajectory": [
                {"lat": 319348552, "lon": 1188222625},
                {"lat": 319348562, "lon": 1188222624},
                {"lat": 319348580, "lon": 1188222623},
                {"lat": 319348607, "lon": 1188222621},
                {"lat": 319348643, "lon": 1188222619},
            ],
            "ptcPredictedTrajectory": [
                {"lat": 319348726, "lon": 1188222614},
                {"lat": 319348864, "lon": 1188222607},
                {"lat": 319349057, "lon": 1188222598},
                {"lat": 319349304, "lon": 1188222586},
                {"lat": 319349605, "lon": 1188222572},
                {"lat": 319349961, "lon": 1188222555},
            ],
            "ptcTrackTimeStamp": 1691119595439,
            "ptcSize": {"width": 180, "length": 500, "height": 30},
            "ptcHeading": 254,
            "ptcAngleSpeed": 0,
        },
    ],
    "obstacles": [],
}
show_info = {
    "type": "SDS",
    "ego_point": {"x": 85.15827080607414, "y": 28.79520247504115},
    "other_cars": [
        {"x": 79.20450179095745, "y": 23.19442876783371},
        {"x": 78.6285520773635, "y": 34.786079659105894},
        {"x": 82.87660262678861, "y": 2.068925358594954},
    ],
}


def http_test():
    import requests

    response = requests.post(
        url="http://127.0.0.1:28304/sensor_data_sharing",
        json={
            "motor_kinematics": motor_traj,
            "vptc_kinematics": vptc_traj,
            "rsi": rsi,
            "msg_VIR": params,
            "sensor_pos": sensor_pos,
            "transform_info": convert_info,
        },
    )

    res = response.json()
    msg_ = res.get("msg")
    show_info_ = res.get("info")
    msg["secMark"] = msg_["secMark"]
    for i, v in enumerate(msg_["participants"]):
        msg["participants"][i]["ptcTrackTimeStamp"] = v["ptcTrackTimeStamp"]
    print(msg_ == msg)
    print(show_info_ == show_info)


def grpc_test():
    import grpc
    from sensor_data_sharing_service.grpc_server import (
        sensor_data_sharing_grpc_pb2_grpc,
        sensor_data_sharing_grpc_pb2,
    )
    import json

    with grpc.insecure_channel("127.0.0.1:28305") as channel:
        stub = sensor_data_sharing_grpc_pb2_grpc.SensorDataSharingGrpcStub(
            channel
        )
        response = stub.sensor_data_sharing(
            sensor_data_sharing_grpc_pb2.SensorDataSharingRequest(
                data=json.dumps(
                    {
                        "motor_kinematics": motor_traj,
                        "vptc_kinematics": vptc_traj,
                        "rsi": rsi,
                        "msg_VIR": params,
                        "sensor_pos": sensor_pos,
                        "transform_info": convert_info,
                    }
                )
            )
        )
        res = json.loads(response.data)
        msg_ = res.get("msg")
        show_info_ = res.get("info")
        msg["secMark"] = msg_["secMark"]
        for i, v in enumerate(msg_["participants"]):
            msg["participants"][i]["ptcTrackTimeStamp"] = v[
                "ptcTrackTimeStamp"
            ]
        print(msg_ == msg)
        print(show_info_ == show_info)


async def ws_test():
    from websockets.client import connect
    import json

    async with connect(
        "ws://127.0.0.1:28304/ws",
    ) as websocket:
        await websocket.send(
            json.dumps(
                {
                    "motor_kinematics": motor_traj,
                    "vptc_kinematics": vptc_traj,
                    "rsi": rsi,
                    "msg_VIR": params,
                    "sensor_pos": sensor_pos,
                    "transform_info": convert_info,
                }
            )
        )
        data = await websocket.recv()
        res = json.loads(data)
        msg_ = res.get("msg")
        show_info_ = res.get("info")
        msg["secMark"] = msg_["secMark"]
        for i, v in enumerate(msg_["participants"]):
            msg["participants"][i]["ptcTrackTimeStamp"] = v[
                "ptcTrackTimeStamp"
            ]
        print(msg_ == msg)
        print(show_info_ == show_info)


if __name__ == "__main__":
    # http_test()
    # grpc_test()
    # asyncio.run(ws_test())

    from algo_lib import SensorDataSharing

    obj = SensorDataSharing()
    msg_, show_info_ = obj.run(
        motor_kinematics=motor_traj,
        vptc_kinematics=vptc_traj,
        rsi=rsi,
        msg_VIR=params,
        sensor_pos=sensor_pos,
        transform_info=convert_info,
    )
    msg["secMark"] = msg_["secMark"]
    for i, v in enumerate(msg_["participants"]):
        msg["participants"][i]["ptcTrackTimeStamp"] = v["ptcTrackTimeStamp"]
    print(msg_ == msg)
    print(show_info_ == show_info)
