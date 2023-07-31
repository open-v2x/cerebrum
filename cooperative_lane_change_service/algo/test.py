import asyncio

with open("data.txt", "r") as f:
    context_frames = eval(f.readline())
    current_frame = eval(f.readline())

params = {
    "msgCnt": "2",
    "id": "68",
    "refPos": {"lon": 1188222000, "lat": 319352246, "ele": 100},
    "secMark": 54400,
    "timeStamp": 1653016794400,
    "intAndReq": {
        "currentBehavior": 2,
        "reqs": {
            "reqID": 10,
            "status": 2,
            "targetRSU": "R328328",
            "info": {
                "laneChange": {
                    "upstreamNode": "",
                    "downstreamNode": "",
                    "targetLane": 17,
                }
            },
            "lifeTime": 500,
        },
    },
}
convert_info = [40388545, 3535296]

msg_rsc = {
    "msgCnt": "2",
    "id": "68",
    "secMark": 54400,
    "refPos": {"lon": 1188222000, "lat": 319352246, "ele": 100},
    "coordinates": {
        "vehId": "68",
        "driveSuggestion": {"suggestion": 2, "lifeTime": 800},
        "pathGuidance": [
            {
                "pos": {"lon": 1188221774, "lat": 319352123, "ele": 100},
                "speed": 237,
                "heading": 14620,
                "estimatedTime": 53900,
            },
            {
                "pos": {"lon": 1188221771, "lat": 319352169, "ele": 100},
                "speed": 259,
                "heading": 14620,
                "estimatedTime": 54000,
            },
            {
                "pos": {"lon": 1188221768, "lat": 319352220, "ele": 100},
                "speed": 280,
                "heading": 14620,
                "estimatedTime": 54100,
            },
            {
                "pos": {"lon": 1188221764, "lat": 319352274, "ele": 100},
                "speed": 302,
                "heading": 14620,
                "estimatedTime": 54200,
            },
            {
                "pos": {"lon": 1188221760, "lat": 319352333, "ele": 100},
                "speed": 323,
                "heading": 14620,
                "estimatedTime": 54300,
            },
            {
                "pos": {"lon": 1188221756, "lat": 319352395, "ele": 100},
                "speed": 345,
                "heading": 14620,
                "estimatedTime": 54400,
            },
            {
                "pos": {"lon": 1188221751, "lat": 319352461, "ele": 100},
                "speed": 366,
                "heading": 14620,
                "estimatedTime": 54500,
            },
            {
                "pos": {"lon": 1188221746, "lat": 319352531, "ele": 100},
                "speed": 388,
                "heading": 14620,
                "estimatedTime": 54600,
            },
            {
                "pos": {"lon": 1188221741, "lat": 319352604, "ele": 100},
                "speed": 409,
                "heading": 14620,
                "estimatedTime": 54700,
            },
            {
                "pos": {"lon": 1188221736, "lat": 319352682, "ele": 100},
                "speed": 431,
                "heading": 14620,
                "estimatedTime": 54800,
            },
            {
                "pos": {"lon": 1188221730, "lat": 319352763, "ele": 100},
                "speed": 452,
                "heading": 14620,
                "estimatedTime": 54900,
            },
            {
                "pos": {"lon": 1188221724, "lat": 319352849, "ele": 100},
                "speed": 473,
                "heading": 14620,
                "estimatedTime": 55000,
            },
            {
                "pos": {"lon": 1188221718, "lat": 319352938, "ele": 100},
                "speed": 495,
                "heading": 14620,
                "estimatedTime": 55100,
            },
            {
                "pos": {"lon": 1188221712, "lat": 319353031, "ele": 100},
                "speed": 516,
                "heading": 14620,
                "estimatedTime": 55200,
            },
            {
                "pos": {"lon": 1188221705, "lat": 319353128, "ele": 100},
                "speed": 538,
                "heading": 14620,
                "estimatedTime": 55300,
            },
            {
                "pos": {"lon": 1188221698, "lat": 319353229, "ele": 100},
                "speed": 559,
                "heading": 14620,
                "estimatedTime": 55400,
            },
            {
                "pos": {"lon": 1188221691, "lat": 319353333, "ele": 100},
                "speed": 581,
                "heading": 14620,
                "estimatedTime": 55500,
            },
            {
                "pos": {"lon": 1188221683, "lat": 319353442, "ele": 100},
                "speed": 602,
                "heading": 14620,
                "estimatedTime": 55600,
            },
            {
                "pos": {"lon": 1188221675, "lat": 319353554, "ele": 100},
                "speed": 624,
                "heading": 14620,
                "estimatedTime": 55700,
            },
            {
                "pos": {"lon": 1188221667, "lat": 319353670, "ele": 100},
                "speed": 645,
                "heading": 14620,
                "estimatedTime": 55800,
            },
            {
                "pos": {"lon": 1188221659, "lat": 319353790, "ele": 100},
                "speed": 666,
                "heading": 14620,
                "estimatedTime": 55900,
            },
            {
                "pos": {"lon": 1188221651, "lat": 319353914, "ele": 100},
                "speed": 688,
                "heading": 14620,
                "estimatedTime": 56000,
            },
            {
                "pos": {"lon": 1188221642, "lat": 319354042, "ele": 100},
                "speed": 709,
                "heading": 14620,
                "estimatedTime": 56100,
            },
            {
                "pos": {"lon": 1188221633, "lat": 319354174, "ele": 100},
                "speed": 731,
                "heading": 14620,
                "estimatedTime": 56200,
            },
            {
                "pos": {"lon": 1188221623, "lat": 319354309, "ele": 100},
                "speed": 752,
                "heading": 14620,
                "estimatedTime": 56300,
            },
            {
                "pos": {"lon": 1188221614, "lat": 319354449, "ele": 100},
                "speed": 774,
                "heading": 14620,
                "estimatedTime": 56400,
            },
            {
                "pos": {"lon": 1188221604, "lat": 319354592, "ele": 100},
                "speed": 795,
                "heading": 14620,
                "estimatedTime": 56500,
            },
            {
                "pos": {"lon": 1188221594, "lat": 319354739, "ele": 100},
                "speed": 817,
                "heading": 14620,
                "estimatedTime": 56600,
            },
            {
                "pos": {"lon": 1188221583, "lat": 319354890, "ele": 100},
                "speed": 838,
                "heading": 14620,
                "estimatedTime": 56700,
            },
            {
                "pos": {"lon": 1188221572, "lat": 319355045, "ele": 100},
                "speed": 860,
                "heading": 14620,
                "estimatedTime": 56800,
            },
        ],
        "info": 0,
    },
}
show_info = {
    "type": "CLC",
    "ego_point": {"x": 75.33169452088946, "y": 40.27393493002538},
    "traj_list_for_show": [
        {"x": 75.33169452088946, "y": 40.27393493002538},
        {"x": 75.3088569317133, "y": 40.74938676199222},
        {"x": 75.28396111562586, "y": 41.26768846519648},
        {"x": 75.25700707262713, "y": 41.82884003963816},
        {"x": 75.22799480271713, "y": 42.43284148531726},
        {"x": 75.19692430589585, "y": 43.079692802233794},
        {"x": 75.16379558216329, "y": 43.76939399038775},
        {"x": 75.12860863151944, "y": 44.501945049779124},
        {"x": 75.09136345396432, "y": 45.27734598040792},
        {"x": 75.05206004949792, "y": 46.09559678227414},
        {"x": 75.01069841812024, "y": 46.956697455377785},
        {"x": 74.96727855983129, "y": 47.86064799971885},
        {"x": 74.92180047463104, "y": 48.807448415297344},
        {"x": 74.87426416251952, "y": 49.79709870211326},
        {"x": 74.82466962349672, "y": 50.8295988601666},
        {"x": 74.77301685756264, "y": 51.90494888945736},
        {"x": 74.71930586471727, "y": 53.02314878998554},
        {"x": 74.66353664496063, "y": 54.184198561751145},
        {"x": 74.6057091982927, "y": 55.38809820475417},
        {"x": 74.5458235247135, "y": 56.63484771899463},
        {"x": 74.48387962422302, "y": 57.924447104472506},
        {"x": 74.41987749682126, "y": 59.256896361187806},
        {"x": 74.35381714250822, "y": 60.63219548914053},
        {"x": 74.2856985612839, "y": 62.05034448833067},
        {"x": 74.2155217531483, "y": 63.51134335875824},
        {"x": 74.14328671810141, "y": 65.01519210042323},
        {"x": 74.06899345614325, "y": 66.56189071332565},
        {"x": 73.9926419672738, "y": 68.15143919746549},
        {"x": 73.91423225149308, "y": 69.78383755284275},
        {"x": 73.83376430880107, "y": 71.45908577945744},
        {"x": 73.75123813919778, "y": 73.17718387730955},
    ],
}


def http_test():
    import requests

    response = requests.post(
        url="http://127.0.0.1:28304/cooperative_lane_change",
        json={
            "transform_info": convert_info,
            "context_frames": context_frames,
            "latest_frame": current_frame,
            "msg_vir": params,
        },
    )
    res = response.json()
    print(res.get("msg") == msg_rsc)
    print(res.get("info") == show_info)


def grpc_test():
    import grpc
    from cooperative_lane_change_service.grpc_server import (
        cooperative_lane_change_grpc_pb2_grpc,
        cooperative_lane_change_grpc_pb2,
    )
    import json

    with grpc.insecure_channel("127.0.0.1:28305") as channel:
        stub = cooperative_lane_change_grpc_pb2_grpc.CooperativeLaneChangeGrpcStub(
            channel
        )
        response = stub.cooperative_lane_change(
            cooperative_lane_change_grpc_pb2.CooperativeLaneChangeRequest(
                data=json.dumps(
                    {
                        "transform_info": convert_info,
                        "context_frames": context_frames,
                        "latest_frame": current_frame,
                        "msg_vir": params,
                    }
                )
            )
        )
        res = json.loads(response.data)
        print(res.get("msg") == msg_rsc)
        print(res.get("info") == show_info)


async def ws_test():
    from websockets.client import connect
    import json

    async with connect(
        "ws://127.0.0.1:28304/ws",
    ) as websocket:
        await websocket.send(
            json.dumps(
                {
                    "transform_info": convert_info,
                    "context_frames": context_frames,
                    "latest_frame": current_frame,
                    "msg_vir": params,
                }
            )
        )
        data = await websocket.recv()
        res = json.loads(data)
        print(res.get("msg") == msg_rsc)
        print(res.get("info") == show_info)


if __name__ == "__main__":
    http_test()
    grpc_test()
    asyncio.run(ws_test())

    # from algo_lib import CooperativeLaneChange
    #
    # change = CooperativeLaneChange()
    # msg_rsc_,show_info_=change.run(
    #     transform_info=convert_info,
    #     context_frames=context_frames,
    #     latest_frame=current_frame,
    #     msg_vir=params,
    # )
    # print(msg_rsc_==msg_rsc)
    # print(show_info_==show_info)
