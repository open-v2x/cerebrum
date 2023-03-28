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

"""Post-process Algorithm.

1. coordinate_transform
2. data convert and generate
3. http

"""

import aiohttp
from common import consts
from common import db
import math
from pyproj import Transformer
from typing import Dict

coord_unit = consts.CoordinateUnit


def choose_epsg(lon: float):
    """Choose a projected coordinate system."""
    for i in range(21):
        if abs(lon - (75 + 3 * i)) < 1.5:
            return "epsg:" + str(i + 2370)


def coordinate_tf(lat, lon, tf, unit=coord_unit) -> tuple:
    """Convert latitude and longitude to geodetic coordinates."""
    return tf.transform(lat / unit, lon / unit)  # y, x


def coordinate_tf_inverse(y, x, tf, unit=coord_unit) -> tuple:
    """Convert geodetic coordinates to latitude and longitude."""
    # 平面坐标 -->  经纬度坐标
    lat, lon = tf.transform(y, x, direction="INVERSE")
    if type(lat) == float:
        return int(lat * unit), int(lon * unit)
    return (lat * unit).astype(int), (lon * unit).astype(int)


def rsm2frame(raw_rsm: dict, rsu_id: str) -> dict:
    """Convert rsm to frame."""
    # rsm数据的数据结构 --> 算法需要的数据结构
    latest_frame = {}
    for rsm in raw_rsm["content"]["rsms"]:
        for pinfo in rsm["participants"]:
            y, x = coordinate_tf(
                pinfo["pos"]["lat"], pinfo["pos"]["lon"], TfMap[rsu_id]
            )
            latest_frame[pinfo["global_track_id"]] = {
                "secMark": pinfo["secMark"],
                "ptcType": pinfo["ptcType"],
                "x": x - XOrigin[rsu_id],
                "y": y - YOrigin[rsu_id],
                "speed": pinfo["speed"],
                "heading": pinfo["heading"],
                "global_track_id": pinfo["global_track_id"],
                "refPos_lat": rsm["refPos"]["lat"],
                "refPos_lon": rsm["refPos"]["lon"],
                "refPos_ele": rsm["refPos"]["ele"],
                "lat": pinfo["pos"]["lat"],
                "lon": pinfo["pos"]["lon"],
                "ele": pinfo["pos"]["ele"],
                "ptcId": pinfo["ptcId"],
                "source": pinfo["source"],
                "lane": pinfo.get("lane"),
            }
            if pinfo.get("size"):
                latest_frame[pinfo["global_track_id"]]["width"] = pinfo.get(
                    "size"
                )["width"]
                latest_frame[pinfo["global_track_id"]]["length"] = pinfo.get(
                    "size"
                )["length"]
                latest_frame[pinfo["global_track_id"]]["height"] = pinfo.get(
                    "size"
                )["height"]
    return latest_frame


def frame2rsm(latest_frame: dict, raw_rsm: dict, rsu_id: str) -> dict:
    """Convert frame to rsm."""
    # 算法数据的数据结构 --> rsm 数据结构
    final_rsm = {
        "name": raw_rsm["name"],
        "id": raw_rsm["id"],
        "content": {"rsms": []},
    }
    device_lat_list = [
        [i["refPos_lat"], i["refPos_lon"], i["refPos_ele"]]
        for i in latest_frame.values()
    ]
    info_dic: Dict[float, dict] = {}  # 多个设备
    for i in device_lat_list:
        info_dic[i[0]] = {
            "refPos": {"lat": i[0], "lon": i[1], "ele": i[2]},
            "participants": [],
        }
    for latest_info in latest_frame.values():
        lat, lon = coordinate_tf_inverse(
            latest_info["y"] + YOrigin[rsu_id],
            latest_info["x"] + XOrigin[rsu_id],
            TfMap[rsu_id],
        )
        obj_info = {
            "ptcType": latest_info["ptcType"],
            "ptcId": latest_info["ptcId"],
            "global_track_id": latest_info["global_track_id"],
            "source": latest_info["source"],
            "secMark": latest_info["secMark"],
            "pos": {"lat": lat, "lon": lon, "ele": latest_info["refPos_ele"]},
            "speed": latest_info["speed"],
            "heading": latest_info["heading"],
            "lane": latest_info["lane"],
        }
        if latest_info.get("refPos_ele"):
            obj_info["pos"]["ele"] = latest_info["refPos_ele"]
        if latest_info.get("width"):
            if not obj_info.get("size"):
                obj_info["size"] = {}
            obj_info["size"]["width"] = latest_info["width"]
        if latest_info.get("length"):
            if not obj_info.get("size"):
                obj_info["size"] = {}
            obj_info["size"]["length"] = latest_info["length"]
        if latest_info.get("height"):
            if not obj_info.get("size"):
                obj_info["size"] = {}
            obj_info["size"]["height"] = latest_info["height"]
        info_dic[latest_info["refPos_lat"]]["participants"].append(obj_info)
    final_rsm["content"]["rsms"] += list(info_dic.values())

    return final_rsm


def convert_for_visual(frame: dict, rsu_id: str) -> None:
    """Coordinate translation and rotation."""
    k = -1 if rsu_info[rsu_id]["reverse"] else 1
    x = frame["x"] + rsu_info[rsu_id]["bias_x"]
    y = k * (frame["y"] - rsu_info[rsu_id]["bias_y"])
    rotation = math.radians(rsu_info[rsu_id]["rotation"])
    new_x = x * math.cos(rotation) - y * math.sin(rotation)
    new_y = x * math.sin(rotation) + y * math.cos(rotation)
    frame["x"] = int(new_x / rsu_info[rsu_id]["scale"])
    frame["y"] = int(new_y / rsu_info[rsu_id]["scale"])


def convert_for_collision_visual(info: list, rsu_id: str) -> None:
    """Coordinate translation and rotation for collision."""
    k = -1 if rsu_info[rsu_id]["reverse"] else 1
    rotation = math.radians(rsu_info[rsu_id]["rotation"])
    for i in range(len(info)):
        for name in ["ego", "other"]:
            x = info[i][name + "_current_point"][0]
            y = info[i][name + "_current_point"][1]
            x += rsu_info[rsu_id]["bias_x"]
            y = k * (y - rsu_info[rsu_id]["bias_y"])
            new_x = x * math.cos(rotation) - y * math.sin(rotation)
            new_y = x * math.sin(rotation) + y * math.cos(rotation)
            info[i][name + "_current_point"][0] = int(
                new_x / rsu_info[rsu_id]["scale"]
            )
            info[i][name + "_current_point"][1] = int(
                new_y / rsu_info[rsu_id]["scale"]
            )


def convert_for_reverse_visual(info: list, rsu_id: str) -> None:
    """Reverse."""
    k = -1 if rsu_info[rsu_id]["reverse"] else 1
    rotation = math.radians(rsu_info[rsu_id]["rotation"])
    for i in range(len(info)):
        x = info[i]["ego_current_point"][0]
        y = info[i]["ego_current_point"][1]
        x += rsu_info[rsu_id]["bias_x"]
        y = k * (y - rsu_info[rsu_id]["bias_y"])
        new_x = x * math.cos(rotation) - y * math.sin(rotation)
        new_y = x * math.sin(rotation) + y * math.cos(rotation)
        info[i]["ego_current_point"][0] = int(
            new_x / rsu_info[rsu_id]["scale"]
        )
        info[i]["ego_current_point"][1] = int(
            new_y / rsu_info[rsu_id]["scale"]
        )


def convert_for_congestion_visual(info: list, rsu: str) -> None:
    """Congestion."""
    k = -1 if rsu_info[rsu]["reverse"] else 1
    rotation = math.radians(rsu_info[rsu]["rotation"])
    for i in range(len(info)):
        # 起点经纬度
        x = info[i]["startPoint"]["x"]
        y = info[i]["startPoint"]["y"]
        x += rsu_info[rsu]["bias_x"]
        y = k * (y - rsu_info[rsu]["bias_y"])
        new_x = x * math.cos(rotation) - y * math.sin(rotation)
        new_y = x * math.sin(rotation) + y * math.cos(rotation)
        info[i]["startPoint"]["x"] = int(new_x / rsu_info[rsu]["scale"])
        info[i]["startPoint"]["y"] = int(new_y / rsu_info[rsu]["scale"])
        # 终点经纬度
        x_end = info[i]["endPoint"]["x"]
        y_end = info[i]["endPoint"]["y"]
        x_end += rsu_info[rsu]["bias_x"]
        y_end = k * (y_end - rsu_info[rsu]["bias_y"])
        new_x_end = x_end * math.cos(rotation) - y_end * math.sin(rotation)
        new_y_end = x_end * math.sin(rotation) + y_end * math.cos(rotation)
        info[i]["endPoint"]["x"] = int(new_x_end / rsu_info[rsu]["scale"])
        info[i]["endPoint"]["y"] = int(new_y_end / rsu_info[rsu]["scale"])


def generate_cwm(cwm_list: list, rsu_id: str) -> dict:
    """Generate collision warning message."""
    position_info = rsu_info[rsu_id]["pos"].copy()
    position_info["lon"] = int(position_info["lon"] * consts.CoordinateUnit)
    position_info["lat"] = int(position_info["lat"] * consts.CoordinateUnit)
    cwm = {
        "targetRSU": rsu_id,
        "sensorPos": position_info,
        "content": cwm_list,
    }
    return cwm


def generate_rdw(rdw_list: list, rsu_id: str) -> dict:
    """Generate reverse driving warning message."""
    position_info = rsu_info[rsu_id]["pos"].copy()
    position_info["lon"] = int(position_info["lon"] * consts.CoordinateUnit)
    position_info["lat"] = int(position_info["lat"] * consts.CoordinateUnit)
    rdw = {
        "targetRSU": rsu_id,
        "sensorPos": position_info,
        "content": rdw_list,
    }
    return rdw


def generate_osw(rdw_list: list, rsu_id: str) -> dict:
    """Generate overspeed warning message."""
    position_info = rsu_info[rsu_id]["pos"].copy()
    position_info["lon"] = int(position_info["lon"] * consts.CoordinateUnit)
    position_info["lat"] = int(position_info["lat"] * consts.CoordinateUnit)
    rdw = {
        "targetRSU": rsu_id,
        "sensorPos": position_info,
        "content": rdw_list,
    }
    return rdw


async def http_get(url: str, params: dict) -> aiohttp.ClientResponse:
    """Get request data."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 201:
                raise SystemError("HTTP call error")
            return await response.json()


async def http_post(url: str, body: dict) -> aiohttp.ClientResponse:
    """Send data to the central platform."""
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=body) as response:
            if response.status != 201:
                raise SystemError("HTTP call error")
            return await response.json()


def generate_transformation_info(refPos: dict):
    """Generate transformation info."""
    for rsu in rsu_info.keys():
        TfMap[rsu] = Transformer.from_crs("epsg:4326", "epsg:2416")

        YOrigin[rsu], XOrigin[rsu] = coordinate_tf(
            refPos["lat"] * coord_unit,
            refPos["lon"] * coord_unit,
            TfMap[rsu],
        )
        XOrigin[rsu] = int(XOrigin[rsu])
        YOrigin[rsu] = int(YOrigin[rsu])


YOrigin: Dict[str, int] = {}
XOrigin: Dict[str, int] = {}
TfMap = {}  # type: ignore

rsu_info = db.rsu_info
refPos = db.refPos
lane_info = db.lane_info
speed_limits = db.speed_limits

db.get_rsu_info(False)
# Get map: refPos + lane_info + speed_limits
db.get_map_info()

rsu_info = {
    "R328328": {
        "pos": {"lon": 118.8213963998, "lat": 31.9348466377},
        "bias_x": 0.0,
        "bias_y": 0.0,
        "rotation": 0.0,
        "reverse": False,
        "scale": 0.09,
    }
}

for item in rsu_info:
    rsu_info[item]["pos"]["lon"]=refPos["lon"] 
    rsu_info[item]["pos"]["lat"]=refPos["lat"]

generate_transformation_info(refPos)
