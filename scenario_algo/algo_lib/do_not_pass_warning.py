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

"""Scenario of Do Not Pass Warning."""

import numpy as np
from post_process_algo import post_process
from typing import Any
from typing import Dict


class Base:
    """Super class of DoNotPass class."""

    def run(
        self,
        rsu_id: str,
        context_frame: dict = {},
        latest_frame: dict = {},
        msg_VIR: dict = {},
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class DoNotPass(Base):
    """Scenario of Do Not Pass Warning.

    Structural logic:
    1. Match the main vehicle ID according to the latitude and longitude of the
       vehicle
    2. Check and calculate the minimum TTC of the most collision risk vehicle
       in the target lane of the host vehicle's lane change intention
    3. Determine whether the main vehicle under this TTC is sufficient to
       complete the reverse overtaking, if not, return the risk information

    """

    OvertakingTime = 9000
    MinTrackLength = 3

    def run(
        self,
        rsu_id: str,
        context_frame: dict = {},
        latest_frame: dict = {},
        msg_VIR: dict = {},
    ) -> tuple:
        """External call function.

        Input:
        context_frames : dict
        It is dict of history track data.

        latest_frame : dict
        It is the latest data obtain from RSU.

        msg_VIR : dict
        It is vehicle's lane-changing requirements from OBU

        transform_info:
        Information required for the conversion of latitude and longitude to
        the geodetic coordinate system

        rsu_id:
        RSU ID for getting the map info

        Output:
        msg_rsc : dict

        show_info: dict
        information for visualization

        """
        # 检测到逆行变道车的转向灯信息(Msg_VIR) 变道前发请求，或者绑定扳动转向灯
        msg_rsc: Dict[str, Any] = {
            "msgCnt": "",
            "id": "",
            "secMark": 0,
            "refPos": {},
            "coordinates": {
                "vehId": "",
                "driveSuggestion": {
                    "suggestion": -1,
                    "lifeTime": 0,
                },
                "pathGuidance": [],
                "info": 0,
            },
        }
        self._rsu_id = rsu_id
        self.context_frame = context_frame
        self.latest_frame = latest_frame
        self.msg_VIR = msg_VIR
        rtg = self._if_retrograde()  # rtg is retrograde: bool
        if not rtg:  # 并非逆行
            return msg_rsc, {}

        # 找到逆行车要去的车道的所有来向车，计算ttc
        risk_veh, risk_ttc = self._potential_risk()
        operation = 1
        effect = self.OvertakingTime

        # 判断ttc是否小于超车所需时间（9s），判断风险
        if risk_ttc < self.OvertakingTime:
            operation = 0
            effect = risk_ttc
        msg_rsc, show_info = self._suggests_generation(effect, operation)

        return msg_rsc, show_info

    def _get_direction(self, lane):
        # 用于获取地图车道的方向，这里预先设定，后续要和地图预设链接。
        return post_process.lane_info[self._rsu_id][lane]

    def _get_id(self):
        lon = self.msg_VIR["refPos"]["lon"]
        lat = self.msg_VIR["refPos"]["lat"]
        veh_id = ""
        min_dis = 1000000000
        for veh in self.latest_frame:
            if self.latest_frame[veh]["ptcType"] != "motor":
                continue
            dis = np.sqrt(
                (lon - self.latest_frame[veh]["lon"]) ** 2
                + (lat - self.latest_frame[veh]["lat"]) ** 2
            )
            if dis < min_dis:
                min_dis = dis
                veh_id = veh
        return veh_id

    def _if_retrograde(self):
        # 找到当前msg车辆车道
        # 找到目标车道
        # 判断是否是逆行超车
        self.veh_id = self._get_id()
        if self.veh_id == "":
            return False
        if "lane" not in self.latest_frame[self.veh_id]:
            return False
        c_lane = self.latest_frame[self.veh_id]["lane"]
        a_lane = self.msg_VIR["intAndReq"]["reqs"]["info"]["retrograde"][
            "targetLane"
        ]
        if self._get_direction(c_lane) * self._get_direction(a_lane) < 0:
            self.aim_lane = a_lane
            return True
        return False

    def _distance(self, veh1, veh2):
        dx = veh1["x"] - veh2["x"]
        dy = veh1["y"] - veh2["y"]
        return np.sqrt(dx**2 + dy**2)

    def _get_v(self, ID):
        if len(self.context_frame[ID]) < self.MinTrackLength:
            return self.latest_frame[ID]["speed"]
        dis = self._distance(self.latest_frame[ID], self.context_frame[ID][-3])
        dt = (
            self.latest_frame[ID]["timeStamp"]
            - self.context_frame[ID][-3]["timeStamp"]
        )
        return dis / dt * 1000  # 米每秒

    def _predict_ttc(self, id1: str, id2: str) -> float:
        if_lead = 1
        x1 = self.latest_frame[id1]["x"]
        y1 = self.latest_frame[id1]["y"]
        x2 = self.latest_frame[id2]["x"]
        y2 = self.latest_frame[id2]["y"]
        vect = np.array([x1 - x2, y1 - y2])
        vec0 = np.array([0, -1])
        l_vect = np.sqrt(vect.dot(vect))
        l_vec0 = np.sqrt(vec0.dot(vec0))
        cos_ = (vect.dot(vec0)) / (l_vect * l_vec0)
        angle = np.arccos(cos_) * 180 / np.pi / 0.0125  # type: ignore
        angle0 = self.latest_frame[id1]["heading"]
        delta_angle = abs(angle - angle0)
        if delta_angle > 90 / 0.0125:  # 如果是锐角
            if_lead = -1
        dis = self._distance(self.latest_frame[id1], self.latest_frame[id2])
        ttc = dis / (self._get_v(id2) + self._get_v(id1)) * (if_lead)
        return ttc * 1000

    def _potential_risk(self) -> tuple:
        # 目标车道所有车辆，和当前车计算：
        # 判断前后，如果已通过则continue
        # 如果迎面，距离 -> TTC -> 记录TTC
        risk_veh = ""
        risk_ttc = 100000.0
        for veh_temp in self.latest_frame:
            if self.latest_frame[veh_temp]["ptcType"] != "motor":
                continue
            if self.latest_frame[veh_temp]["lane"] == self.aim_lane:
                ttc = self._predict_ttc(self.veh_id, veh_temp)
                if ttc < risk_ttc and ttc > 0:
                    risk_veh = veh_temp
                    risk_ttc = ttc
        return risk_veh, risk_ttc

    def _suggests_generation(self, time, operation):
        operation_dic = {1: True, 0: False}
        show_info = {
            "type": "DNP",
            "ego_point": {
                "x": self.latest_frame[self.veh_id]["x"],
                "y": self.latest_frame[self.veh_id]["y"],
            },
            "if_accept": operation_dic[operation],
        }
        effect = time * 0.1
        msg_rsc = {}
        msg_rsc.update(
            {
                "msgCnt": self.msg_VIR["msgCnt"],
                "id": self.msg_VIR["id"],
                "secMark": self.msg_VIR["secMark"],
                "refPos": self.msg_VIR["refPos"],
                "coordinates": {
                    "vehId": self.msg_VIR["id"],
                    "driveSuggestion": {
                        "suggestion": operation,
                        "lifeTime": int(effect),
                    },
                    "pathGuidance": [],
                    "info": 0,
                },
            }
        )
        return msg_rsc, show_info
