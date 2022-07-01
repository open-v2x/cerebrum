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

"""Drivers for different data structure."""

from datetime import datetime
import orjson as json
from transform_driver import consts
from transform_driver.log import Loggings
from typing import Any
from typing import Dict

ADVERSE_WEATHER_CODE = [301, 308, 305, 311, 302, 304, 399]
ABNORMAL_TRAFFIC_CODE = [707, 401, 405, 406, 408, 409, 202, 205]
ADNORMAL_VEHICLE_CODE = [901, 902, 903, 904, 905, 906]
logging = Loggings()


def rsm_std(payload: bytes):
    """Receive data in RSM format."""
    return "ok", json.loads(payload), "ok"


def rsi_std(payload: bytes):
    """Receive data in RSI format."""
    rsi = json.loads(payload)
    # 如果发现拥堵事件，额外记录
    if str(rsi).find('"eventType" : 707,') == -1:
        return rsi, False
    return rsi, True


def rsm_dawnline(payload: bytes):
    """Receive data in dawnline format and convert it to RSM format data."""
    # 接收 mqtt 传来的 rsu_id 和原始数据
    # 根据 rsm 的字段需求，匹配出原始数据的相关数据
    # 如果必要字段缺失，则会直接返回错误
    coord_unit = consts.CoordinateUnit
    miss_optional_flag = False
    try:
        raw = json.loads(payload)
    except BaseException:
        msg_info = "RSM is empty"
        logging.error(msg_info)
        return "miss_required_key", {}, msg_info
    rsm_format: Dict[str, Any] = {
        "name": None,
        "id": None,
        "content": {"rsms": []},
    }
    for original_info in raw:
        rsm_info: Dict[str, Any] = {
            "refPos": {
                "lat": int(original_info["dev_pos"]["lat"] * coord_unit),
                "lon": int(original_info["dev_pos"]["lon"] * coord_unit),
                "ele": None,
            },
            "participants": [],
        }
        if original_info.get("content") is None:
            msg_info = "Missing rsm required key: content"
            logging.error(msg_info)
            return "miss_required_key", {}, msg_info
        for _info in original_info["content"]:
            required_keys = {
                "ptcType": _info.get("ptcType"),
                "global_track_id": _info.get("global_track_id"),
                "timeStamp": _info.get("timeStamp"),
                "pos_lat": _info.get("pos_lat"),
                "pos_lon": _info.get("pos_lon"),
                "heading": _info.get("heading"),
            }
            for required_key, required_value in required_keys.items():
                if required_value is None:
                    msg_info = f"Missing rsm required key: {required_key}"
                    logging.error(msg_info)
                    return "miss_required_key", {}, msg_info
            participant = {
                "ptcType": _info["ptcType"],
                "ptcId": int(float(_info.get("ptcId"))),
                "global_track_id": _info["global_track_id"],
                "source": _info.get("source"),
                "secMark": int(_info["timeStamp"] % consts.MaxSecMark),
                "pos": {
                    "lat": int(_info["pos_lat"] * coord_unit),
                    "lon": int(_info["pos_lon"] * coord_unit),
                    "ele": None,
                },
                "speed": int(_info.get("speed") / 0.02),
                "heading": int(_info["heading"] / 0.0125),
                "lane": _info.get("lane"),
            }
            if _info.get("width"):
                participant["size"] = {
                    "width": int(_info["width"] / 0.01),
                    "length": int(_info["length"] / 0.01),
                    "height": int(_info["height"] / 0.05),
                }
            optional_keys = {
                "ptcId": participant.get("ptcId"),
                "source": participant.get("source"),
                "speed": participant.get("speed"),
                "lane": participant.get("lane"),
                "size": participant.get("size"),
            }
            for optional_key, optional_value in optional_keys.items():
                if optional_value is None:
                    miss_optional_flag = True
                    msg_info = f"Missing rsm optional key: {optional_key}"
            rsm_info["participants"].append(participant)
        rsm_format["content"]["rsms"].append(rsm_info)
    if miss_optional_flag:
        logging.warning(msg_info)
        return "miss_optional_key", rsm_format, msg_info
    return "ok", rsm_format, "ok"


def time_transform(time_stamp: int):
    """Convert time format."""
    return (
        datetime.utcfromtimestamp(time_stamp / 1000).strftime(
            "%Y-%m-%dT%H:%M:%S.%f"
        )[:-3]
        + "Z"
    )


def rsi_dawnline(payload: bytes) -> tuple:
    """Receive data in dawnline format and convert it to RSI format data."""
    event_format = json.loads(payload)
    congestion = False
    rsi = {
        "rsiSourceType": event_format["dev_type"],
        "rsiSourceId": event_format["dev_id"],
        "rsiDatas": [],
    }
    for event_info in event_format["event_content"]:
        rsi_data = {
            "alertID": event_info["event_id"],
            "duration": 0,
            "eventStatus": True,
            "timeStamp": time_transform(event_info["timeStamp"]),
            "eventClass": None,
            "eventType": event_info["event_type"],
            "eventSource": event_info["event_source"],
            "eventPosition": {
                "lat": event_info["latitude"],
                "lon": event_info["longitude"],
            },
        }
        if event_info["event_type"] in ADVERSE_WEATHER_CODE:
            rsi_data["eventClass"] = "AdverseWeather"
        elif event_info["event_type"] in ABNORMAL_TRAFFIC_CODE:
            rsi_data["eventClass"] = "AbnormalTraffic"
        else:
            rsi_data["eventClass"] = "AbnormalVehicle"
        rsi["rsiDatas"].append(rsi_data)
        if event_info["event_type"] == 707:
            congestion = True
    return rsi, congestion
