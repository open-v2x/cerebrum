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

"""Scenario of Cooperative Lane Change."""

import numpy as np
from post_process_algo import post_process


class Base:
    """Super class of CooperativeLaneChange class."""

    def run(
        self,
        transform_info: list,
        context_frames: dict = {},
        latest_frame: dict = {},
        msg_VIR: dict = {},
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class CooperativeLaneChange(Base):
    """Scenario of Cooperative Lane Change.

    Structural logic:
    1. Match the ego vehicle ID according to the vehicle's latitude and
       longitude position
    2. Filter IDs of surrounding vehicles in the same lane and adjacent lanes
       of the host vehicle
    3. Determine whether there is a lane change risk,
       and if so, return the risk information
    4. The risk-free vehicle is recommended to limit the initial speed of lane
       change by the front and rear vehicles in the current lane
    5. The lane change termination speed is limited by the target lane vehicle
       speed
    6. Limit vehicle steering heading angle based on current vehicle distance
    7. Integrate 4, 5, and 6 to generate planned paths and return vehicle
       guidance suggestions

    """

    LaneChangeTime = 3000  # 换道用时通常为3s = 3000ms
    SafeTimeTTC = 2000  # 安全的TTC，以饱和车头时距计2s = 2000ms
    MinTrackLength = 3  # 计算速度的历史轨迹点数量
    MinTTC = 10000.0  # 用于记录目标车道最小车头时距的值

    def __init__(self) -> None:
        """Class initialization."""

    def run(
        self,
        transform_info: list,
        context_frames: dict = {},
        latest_frame: dict = {},
        msg_VIR: dict = {},
    ) -> tuple:
        """External call function.

        Input:
        context_frames : dict
        It is dict of history track data

        latest_frame : dict
        It is the latest data obtain from RSU

        msg_VIR : dict
        It is vehicle's lane-changing requirements from OBU

        transform_info:
        Information required for the conversion of latitude and longitude to
        the geodetic coordinate system

        Output:
        msg_rsc : dict

        show_path: dict
        information for visualization

        """
        self._transform_info = transform_info
        self._transformer = self._transform_info[0]
        self.context_frames = context_frames
        self.latest_frame = latest_frame
        self.msg_VIR = msg_VIR
        self.vehId = self._id_get()
        valid = self._if_valid()
        if valid is False:
            self.suggestion = -1
            return self._gener_suggests(-1, path=[]), {}
        self.suggestion = 14  # 14为未协调初始值，协调后会被更改
        self.surround = self._status_acqu()
        # 风险判断
        risk = self._risk_judgment()
        # 建议生成
        return self._suggests_generation(risk)

    def _if_valid(self):
        if self.vehId == "":
            return False
        if "lane" not in self.latest_frame[self.vehId]:
            print("Lane missing, induction cannot be applied")
            return False
        return True

    def _id_get(self):
        lon = self.msg_VIR["refPos"]["lon"]
        lat = self.msg_VIR["refPos"]["lat"]
        veh_id = ""
        min_dis = 10**20
        for veh in self.latest_frame:
            if self.latest_frame[veh]["ptcType"] != "motor":
                continue
            dis = np.sqrt(
                (0.8 * (lon - self.latest_frame[veh]["lon"])) ** 2
                + (lat - self.latest_frame[veh]["lat"]) ** 2
            )  # 单位经纬度代表米范围有差异 (0.8 * lon)/(1 * lat)=1
            if dis < min_dis:
                min_dis = dis
                veh_id = veh
        return veh_id

    def _distance(self, veh1, veh2):
        dx = veh1["x"] - veh2["x"]
        dy = veh1["y"] - veh2["y"]
        return np.sqrt(dx**2 + dy**2)

    def _lane_judge(self, line):
        if "lane" in line:
            return line["lane"]
        return False

    def _status_acqu(self):
        # 把目标车道车辆存入
        # 把发送请求车辆的ID找到
        # 找到一个与当前车同车道的最邻近车，以这个速度作为标准（速度平衡原则
        surround = {"ref_veh": -1, "aim_lane_veh": [], "cut_in_veh": -1}
        veh_lane = self.latest_frame[self.vehId]["lane"]
        nearest = []
        # 判断curr_pkg所有车所在车道
        for key in self.latest_frame:
            if self.latest_frame[key]["ptcType"] != "motor":
                continue
            lane = self._lane_judge(self.latest_frame[key])
            if (
                lane
                == self.msg_VIR["intAndReq"]["reqs"]["info"]["laneChange"][
                    "targetLane"
                ]
            ):
                surround["aim_lane_veh"].append(key)
            elif lane == veh_lane and key != self.vehId:
                dis = self._distance(
                    self.latest_frame[key], self.latest_frame[self.vehId]
                )
                if len(nearest) == 0 or nearest[1] > dis:
                    nearest = [key, dis]
        surround.setdefault("ref_veh", [])
        if len(nearest):
            surround.update({"ref_veh": nearest[0]})
        return surround

    def _get_v(self, ID):
        if len(self.context_frames[ID]) < self.MinTrackLength:
            # v(新四跨)* 0.02 = v (m/s)
            return self.latest_frame[ID]["speed"] * 0.02
        dis = self._distance(
            self.latest_frame[ID], self.context_frames[ID][-3]
        )
        dt = (
            self.latest_frame[ID]["timeStamp"]
            - self.context_frames[ID][-3]["timeStamp"]
        )
        return dis / dt * 1000  # 米每秒

    def _dv(self, id1, id2):
        return self._get_v(id2) - self._get_v(id1)

    def _headway_predict(self, id1: str, id2: str) -> float:
        # 算出id1 -> id2的向量航向角
        # 算出id1的航向角
        # 这两个航向角夹角是锐角，则id2在id1前面，否则在后面。
        if_lead = True
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
        d_angle = abs(angle - angle0)
        if d_angle > 90 / 0.0125:  # 如果是锐角
            if_lead = False
        dis = self._distance(self.latest_frame[id1], self.latest_frame[id2])
        # 当前距离（前+后-） lanchangingtime * (v2-v1)
        # 3s后间距 除以后车速度
        if if_lead:
            curr_dis = dis + self.LaneChangeTime * (self._dv(id1, id2)) / 1000
            return curr_dis / self._get_v(id1) * 1000
        curr_dis = dis - self.LaneChangeTime * (self._dv(id1, id2)) / 1000
        return curr_dis / self._get_v(id2) * 1000

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
        d_angle = abs(angle - angle0)
        if d_angle > 90 / 0.0125:  # 如果不是锐角
            if_lead = -1
        dis = self._distance(self.latest_frame[id1], self.latest_frame[id2])
        dv = self._get_v(id2) - self._get_v(id1)
        if dv == 0:
            dv = 0.00000001
        ttc = dis / dv * (if_lead)
        return ttc * 1000

    def _risk_judgment(self) -> bool:
        risk = False
        for temp_veh in self.surround["aim_lane_veh"]:
            ttc = self._predict_ttc(self.vehId, temp_veh)
            if ttc < self.MinTTC and ttc > 0:
                self.surround.update({"cut_in_veh": temp_veh})
                self.MinTTC = ttc
            if ttc < self.SafeTimeTTC and ttc > 0:
                risk = True
        return risk

    def _plan_path(self, v1: int, v2: int, heading: int):
        c_heading = self.latest_frame[self.vehId]["heading"]
        curr_t = self.latest_frame[self.vehId]["timeStamp"]
        t = np.arange(curr_t, curr_t + 8000, 100)
        last_x = self.latest_frame[self.vehId]["x"]
        last_y = self.latest_frame[self.vehId]["y"]
        path = []
        g_path = []
        g_path.append(
            {
                "x": float(last_x),
                "y": float(last_y),
            }
        )
        plan_num = 30
        for i in range(plan_num):
            v = v1 + (v2 - v1) * i / (plan_num - 1)
            h = int(
                c_heading
                + (heading - c_heading) * np.sin(np.pi * i / (plan_num - 1))
            )
            px = last_x + v * 0.1 * np.sin(h * 0.0125 / 180 * np.pi)
            py = last_y - v * 0.1 * np.cos(h * 0.0125 / 180 * np.pi)
            last_x, last_y = px, py
            g_path.append(
                {
                    "x": float(px),
                    "y": float(py),
                }
            )
            lat, lon = post_process.coordinate_tf_inverse(
                py + self._transform_info[2],
                px + self._transform_info[1],
                self._transformer,
            )
            ele = 100
            pathpos = {
                "pos": {"lon": lon, "lat": lat, "ele": ele},
                "speed": int(v / 0.02),
                "heading": h,
                "estimatedTime": int(t[i]),
            }
            path.append(pathpos)
        return path, g_path

    def _suggests_generation(self, risk: bool):
        if risk:
            self.suggestion = 0
            effect = int(0.1 * self.LaneChangeTime)
            return self._gener_suggests(effect, []), {}
        v1, heading = self._ref_veh_lmt()
        v2 = self._aim_lane_lmt()
        # 生成建议
        eff_t = max(self.MinTTC - self.SafeTimeTTC, 1000)
        effect = int(eff_t * 0.1)
        path, g_path = self._plan_path(v1, v2, heading)
        show_path = {
            "type": "CLC",
            "ego_point": g_path[0],
            "traj_list_for_show": g_path,
        }
        msg_RSC = self._gener_suggests(effect, path)
        return msg_RSC, show_path

    def _ref_veh_lmt(self):
        # 限制v1，和heading
        if self.surround["ref_veh"] == -1:
            return (
                # v(新四跨)* 0.02 = v (m/s)
                self.latest_frame[self.vehId]["speed"] * 0.02,
                self.latest_frame[self.vehId]["heading"],
            )
        ref_speed = self._get_v(self.surround["ref_veh"])
        headway = self._headway_predict(self.vehId, self.surround["ref_veh"])
        if headway < 0:
            headway = 3000
        veh_v = self._get_v(self.vehId)
        d_heading = 0.087  # 车辆默认换道角度为5度左右
        if veh_v != 0:
            # 限制最大换道角度为25度
            # 横向车道: 3m, 速度: v, 车头时距: headway, 时间戳单位换算系数: 1000
            d_heading = min(0.435, np.arctan(3 * 1000 / headway / veh_v))
        d_heading = d_heading * 180 / np.pi / 0.0125
        if self.msg_VIR["intAndReq"]["currentBehavior"] == 1:
            return (
                ref_speed,
                self.latest_frame[self.vehId]["heading"] - d_heading,
            )
        return ref_speed, self.latest_frame[self.vehId]["heading"] + d_heading

    def _aim_lane_lmt(self):
        # 限制执行开始t和执行时效t, self.min_headway,用目标车道车辆ID校验建议速度
        if len(self.surround["aim_lane_veh"]) == 0:
            # v(新四跨)* 0.02 = v (m/s)
            return self.latest_frame[self.vehId]["speed"] * 0.02
        sum_speed = 0
        for k in self.surround["aim_lane_veh"]:
            sum_speed += self._get_v(k)
        ave_speed = sum_speed / len(self.surround["aim_lane_veh"])
        if self.surround["cut_in_veh"] != -1:
            cut_in_speed = self._get_v(self.surround["cut_in_veh"])
            return (cut_in_speed + ave_speed) / 2
        return ave_speed

    def _gener_suggests(self, effect: int, path: list):
        if self.suggestion > 0:
            self.suggestion = self.msg_VIR["intAndReq"]["currentBehavior"]
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
                        "suggestion": int(self.suggestion),
                        "lifeTime": int(effect),
                    },
                    "pathGuidance": path,
                    "info": 0,
                },
            }
        )
        return msg_rsc
