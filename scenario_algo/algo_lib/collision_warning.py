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

"""Collision Warning Algorithm.

1. Intersection Collision Warning
2. Vulnerable Road User Collision Warning

"""

from enum import Enum
from enum import unique
import itertools
import math
import numpy as np
from pre_process_ai_algo.algo_lib import utils as process_tools
from scenario_algo.algo_lib import utils
from typing import List


@unique
class EventType(Enum):
    """Enumeration of supported collision scenarios."""

    Vehicle = 0
    VulnerableTrafficParticipant = 1


@unique
class CollisionType(Enum):
    """Enumeration of collision types."""

    RearEndConflict = 0
    ForwardConflict = 1
    SideConflict = 2


@unique
class TrajectoryPredictModel(Enum):
    """Enumeration of trajectory prediction models."""

    CA = 0  # ConstantAcceleration
    CV = 1  # ConstantVelocity
    CTRA = 2  # ConstantTurnRateAndAcceleration
    CTRV = 3  # ConstantTurnRateAndVelocity


@unique
class ConflictIndex(Enum):
    """Enumeration of supported conflict index."""

    TTC = 0  # TimeToCollision
    PSD = 1  # Proportion of Stopping Distance
    FMRD = 2  # Risk Degree Based on Fuzzy Mathematics


VehicleDefaultLength = 380  # 文档规定单位为厘米
VehicleDefaultWidth = 180  # 文档规定单位为厘米
PedestrianDefaultRadius = 50  # 厘米
NonMotorDefaultRadius = 100  # 厘米
MinDataDuration = 0.5  # 至少有多少秒的数据才计算车辆的动力学信息


class Base:
    """Super class of collision warning class."""

    def run(
        self, context_frames: dict, current_frame: dict, last_timestamp: int
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class CollisionWarning(Base):
    """Collision warning algorithm.

    Scenarios:
    1. Intersection Collision Warning and
    2. Vulnerable Road User Collision Warning

    Structural logic:
    1. Combine historical frame data and current frame data
    2. Filter available historical frame data
    3. Calculate kinematic and future information for participants
    4. Pairs examine participants' future trajectory collisions
    5. Calculate collision conflict index
    6. Judging whether an early warning is required based on the threshold
    7. Determine the type of collision and generate warning information

    """

    def __init__(
        self,
        icw: bool = True,
        vrucw: bool = True,
        predict_duration: float = 3,  # s
        predict_interval: float = 0.5,  # s
        v2v_conflict_index: ConflictIndex = ConflictIndex.TTC,
        v2vptc_conflict_index: ConflictIndex = ConflictIndex.FMRD,
        ttc_threshold: float = 2.14,  # s
        psd_max_dece: float = 3.4,  # m/s^2
        fmrd_threshold: float = 0.4,
        # 根据交叉口视频人工统计，车辆转向时间一般为5-10s
        angular_speed_threshold: float = 0.2,  # rad/s 阈值为8s转90度
        # 理论上加速度阈值应为0，由于检测误差导致每辆车都有加速度，因此设置一定阈值
        # 根据rsu模拟器中rsm_track数据的统计结果，无加速度时加速度一般小于1
        acc_threshold: float = 1,  # m/s^2
    ) -> None:
        """Class initialization.

        icw:
        Whether check Intersection Collision Warning

        vrucw:
        Whether check Vulnerable Road User Collision Warning

        predict_duration:
        Prediction period for the participant's future trajectory

        predict_interval:
        Time interval for future trajectory points

        v2v_conflict_index:
        Conflict index for determining vehicle collisions

        v2vptc_conflict_index:
        Conflict index for judging vehicle collisions with vulnerable
        participants

        ttc_threshold:
        The warning threshold for the indicator of time to collision

        psd_max_dece:
        The maximum deceleration required by Proportion of Stopping Distance

        fmrd_threshold:
        Warning threshold of Risk Degree Based on Fuzzy Mathematics

        angular_speed_threshold:
        The steering rate threshold used to determine the trajectory prediction
        model

        acc_threshold
        Vehicle acceleration threshold used to determine the trajectory
        prediction model

        """
        self._icw = icw
        self._vrucw = vrucw
        self._fmrd_threshold = fmrd_threshold
        self._fmrd_weight = np.mat([0.45, 0.3, 0.25])  # type: ignore
        self._angular_speed_threshold = angular_speed_threshold
        self._acc_threshold = acc_threshold
        # 两参与者轨迹点的距离小于阈值才进行矩形关系判别 m
        self._displacement_threshold = 4
        # 两参与者至少有一个速度大于阈值，才进行碰撞判断 m/s
        self._min_speed_for_checking = 2.8
        # 拟预测多久的未来轨迹，需依据不同轨迹预测模型选择恰当的时间长度
        self._predict_duration = predict_duration
        # 轨迹点的时间间隔，决定未来轨迹的离散程度，决定计算量
        self._predict_interval = predict_interval
        # 选择冲突指标
        self._v2v_conflict_index = v2v_conflict_index
        self._v2vptc_conflict_index = v2vptc_conflict_index
        # 指定各冲突指标的预警阈值
        self._ttc_threshold = ttc_threshold
        self._psd_max_dece = psd_max_dece
        # 未来轨迹点的个数
        self._num_of_traj_points = int(predict_duration / predict_interval)
        # 不同轨迹预测模型用不同的公式计算未来航向角，非恒定曲率 or 恒定曲率
        self._traj_heading_map = {
            TrajectoryPredictModel.CA: self._calc_traj_heading_nctr,
            TrajectoryPredictModel.CV: self._calc_traj_heading_nctr,
            TrajectoryPredictModel.CTRA: self._calc_traj_heading_ctr,
            TrajectoryPredictModel.CTRV: self._calc_traj_heading_ctr,
        }

    def run(
        self, context_frames: dict, current_frame: dict, last_timestamp: int
    ) -> tuple:
        """External call function.

        Input:
        context_frames:
        Algorithm's historical frame data, obtained from the result of the last
        call, AID format

        current_frame:
        latest frame data, AID format

        last_timestamp:
        The current frame data timestamp when the algorithm function was last
        called

        Output:
        collision_warning_message:
        Collision warning message for broadcast, CWM format

        event_list:
        Collision warning information for visualization

        last_timestamp:
        Timestamp of current frame data for the next call

        ptc_info["motors_kinematics"]:
        The kinematic information of the vehicle
        can be used in other scenarios such as sensor data sharing

        vptc_kinematics:
        The kinematic information of the vulnerable participants
        can be used in other scenarios such as sensor data sharing

        """
        self._event_list: List[dict] = []
        self._collision_warning_message: List[dict] = []
        self._current_frame = current_frame
        id_set, last_timestamp = process_tools.frames_combination(
            context_frames, self._current_frame, last_timestamp
        )
        if not (self._icw and self._vrucw):
            return (
                self._collision_warning_message,
                self._event_list,
                last_timestamp,
                {},
                {},
            )
        check_ptc = ["motors"]
        if self._vrucw:
            check_ptc = ["motors", "non_motors", "pedestrians"]
        ptc_info: dict = {"motors": {}, "non_motors": {}, "pedestrians": {}}
        # 分别计算机动车、非机动车、行人的运动学信息，用于检查未来碰撞情况
        motors, non_motors, pedestrians = self._filter_ptcs(
            context_frames, last_timestamp, id_set
        )
        for ptc_type in check_ptc:
            ptc_info[ptc_type + "_kinematics"] = getattr(
                self, "_prepare_{}_kinematics".format(ptc_type)
            )(locals()[ptc_type])
        vptc_kinematics = {
            **ptc_info["non_motors_kinematics"],
            **ptc_info["pedestrians_kinematics"],
        }
        # 计算车辆的运动学信息，用于检查未来碰撞情况
        # 各车辆不重复的两两配对，检查碰撞情况与迫切情况，并生成事件数据
        self._v2v_collision_check(ptc_info["motors_kinematics"])
        self._v2vptc_collision_check(
            ptc_info["motors_kinematics"], vptc_kinematics
        )
        return (
            self._collision_warning_message,
            self._event_list,
            last_timestamp,
            ptc_info["motors_kinematics"],
            vptc_kinematics,
        )

    def _v2v_collision_check(self, motors_info: dict) -> None:
        if not self._icw:
            return None
        for ego_key, other_key in itertools.combinations(
            motors_info.keys(), 2
        ):
            cwm, event = self._predict_motor_pair(
                motors_info[ego_key],
                motors_info[other_key],
            )
            if event:
                self._event_list.append(event)
                self._collision_warning_message.append(cwm)

    def _v2vptc_collision_check(
        self, motors_info: dict, vptc_info: dict
    ) -> None:
        if not self._vrucw:
            return None
        for motor_key, vptc_key in itertools.product(motors_info, vptc_info):
            cwm, event = self._predict_vptc_pair(
                motors_info[motor_key],
                vptc_info[vptc_key],
            )
            if event:
                self._event_list.append(event)
                self._collision_warning_message.append(cwm)

    def _prepare_motors_kinematics(self, motors: dict) -> dict:
        # 返回各个车辆运动学信息的字典
        ret = {}
        for k, mot in motors.items():
            # 关键数据转换为列表存储，方便计算差值、均值等信息
            ret[k] = {
                "x": [v["x"] for v in mot],
                "y": [v["y"] for v in mot],
                "heading": [math.radians(v["heading"] * 0.0125) for v in mot],
                "timeStamp": [(v["timeStamp"] / 1000) for v in mot],
                "length": mot[-1].get("length", VehicleDefaultLength) / 100,
                "width": mot[-1].get("width", VehicleDefaultWidth) / 100,
                "guid": k,
            }
            # 车辆按顺序计算速度加速度、未来轨迹、轨迹航向角以及轨迹足迹（矩形坐标）
            for func_name in (
                "speed_and_acc",
                "traj_point",
                "traj_heading",
                "motor_footprint",
            ):
                getattr(self, "_calc_{}".format(func_name))(ret[k])
        return ret

    def _prepare_non_motors_kinematics(self, non_motors: dict) -> dict:
        # 返回各个非机动车运动学信息的字典
        ret = {}
        for k, non_mot in non_motors.items():
            # 关键数据转换为列表存储，方便计算差值、均值等信息
            ret[k] = {
                "x": [v["x"] for v in non_mot],
                "y": [v["y"] for v in non_mot],
                "heading": [
                    math.radians(v["heading"] * 0.0125) for v in non_mot
                ],
                "timeStamp": [(v["timeStamp"] / 1000) for v in non_mot],
                "radius": NonMotorDefaultRadius / 100,
                "guid": k,
                "ptcType": "non_motor",
            }
            # 非机动车按顺序计算速度加速度、未来轨迹
            for func_name in ("speed_and_acc", "traj_point", "traj_heading"):
                getattr(self, "_calc_{}".format(func_name))(ret[k])
        return ret

    def _prepare_pedestrians_kinematics(self, pedestrians):
        # 返回各个运动学信息的字典
        ret = {}
        for k, ped in pedestrians.items():
            # 关键数据转换为列表存储，方便计算差值、均值等信息
            ret[k] = {
                "x": [v["x"] for v in ped],
                "y": [v["y"] for v in ped],
                "heading": [math.radians(v["heading"] * 0.0125) for v in ped],
                "timeStamp": [(v["timeStamp"] / 1000) for v in ped],
                "radius": PedestrianDefaultRadius / 100,
                "guid": k,
                "ptcType": "pedestrian",
            }
            # 行人按顺序计算速度加速度、未来轨迹
            for func_name in ("speed_and_acc", "traj_point", "traj_heading"):
                getattr(self, "_calc_{}".format(func_name))(ret[k])
        return ret

    def _filter_ptcs(
        self, context_frames: dict, last_timestamp: int, id_set: set
    ) -> tuple:
        timestamp_threshold = last_timestamp - (MinDataDuration * 1000)
        motors = dict()
        non_motors = dict()
        pedestrians = dict()
        for guid, ptc_info in context_frames.items():
            filtered = [
                v
                for v in ptc_info
                if v["timeStamp"] >= timestamp_threshold
                and v["global_track_id"] in id_set
            ]
            if len(filtered) <= 4:
                continue
            if filtered[-1]["timeStamp"] == filtered[-2]["timeStamp"]:
                continue
            if ptc_info[-1]["ptcType"] == "motor":
                motors[guid] = filtered
            elif ptc_info[-1]["ptcType"] == "non-motor":
                non_motors[guid] = filtered
            elif ptc_info[-1]["ptcType"] == "pedestrian":
                pedestrians[guid] = filtered
        return motors, non_motors, pedestrians

    def _predict_motor_pair(self, ego: dict, other: dict) -> tuple:
        if not self._is_valid(ego, other):
            return {}, {}
        ego_traj, other_traj = (
            np.array(ego["traj_point"]),
            np.array(other["traj_point"]),
        )
        ego_fp, other_fp = ego["traj_footprint"], other["traj_footprint"]
        dis = abs(ego_traj - other_traj)
        # 逐轨迹点的时间顺序，判断碰撞，碰撞指两矩形重叠
        for k in range(self._num_of_traj_points):
            if any(
                [
                    dis[k][0] < self._displacement_threshold,
                    dis[k][1] < self._displacement_threshold,
                ]
            ):
                if utils.is_rects_overlapped(ego_fp[k], other_fp[k]):
                    need_w = self._need_warning(ego, k)
                    if need_w:
                        return self._build_v2v_event(ego, other, k)
        return {}, {}

    def _predict_vptc_pair(self, motor: dict, vptc: dict) -> tuple:
        if not self._is_valid(motor, vptc):
            return {}, {}
        motor_traj_np = np.array(motor["traj_point"])
        vptc_traj_np = np.array(vptc["traj_point"])
        dis = np.linalg.norm(  # type: ignore
            motor_traj_np - vptc_traj_np, axis=1
        )
        motor_fp = motor["traj_footprint"]

        overlapped = False
        for k in range(self._num_of_traj_points):
            if dis[k] < self._displacement_threshold:
                if utils.is_rect_and_circle_overlapped(
                    motor_fp[k], vptc["traj_point"][k], vptc["radius"]
                ):
                    overlapped = True
                    break
        if self._v2vptc_conflict_index.name == "FMRD":
            TTC = (
                (k + 1) * self._predict_interval
                if overlapped
                else 1.5 * self._ttc_threshold
            )
            need_w = self._warning_FMRD(motor, dis, TTC)
            if need_w:
                return self._build_v2vptc_event(motor, vptc, k)
        elif overlapped:
            need_w = self._need_warning(motor, k)
            if need_w:
                return self._build_v2vptc_event(motor, vptc, k)
        return {}, {}

    def _need_warning(self, ego: dict, k: int) -> bool:
        return getattr(
            self, "_warning_{}".format(self._v2v_conflict_index.name)
        )(ego, k)

    def _warning_FMRD(self, ego: dict, dis, TTC: float) -> bool:
        TTC_membership = utils.TTCMembership(TTC, self._ttc_threshold)
        # MMD is min_meeting_distance
        MMD_index = np.argmin(dis)
        MMD_membership = utils.MMDMembership(
            float(dis[MMD_index]), ego["speed"], self._psd_max_dece
        )
        # MMS is min_meeting_speed
        MMS = (
            float(dis[MMD_index] - dis[MMD_index - 1]) / self._predict_interval
            if MMD_index != 0
            else -10
        )
        MMS_membership = utils.MMSMembership(MMS, ego["speed"])
        membership = np.mat(  # type: ignore
            [TTC_membership, MMD_membership, MMS_membership]
        )
        fused_membership = self._fmrd_weight * membership
        fused_membership = fused_membership.getA()[0]
        if fused_membership[1] > fused_membership[0]:
            scaled_fused_membership = (fused_membership[1] - 0.5) / 0.5
            if scaled_fused_membership > self._fmrd_threshold:
                return True
        return False

    def _warning_TTC(self, ego: dict, k: int) -> bool:
        TTC = (k + 1) * self._predict_interval
        if TTC < self._ttc_threshold:
            return True
        return False

    def _warning_PSD(self, ego: dict, k: int) -> bool:
        # RD 距碰撞点的距离
        RD_x = ego["traj_point"][k][0] - ego["x"][-1]
        RD_y = ego["traj_point"][k][1] - ego["y"][-1]
        # 按最大减速度，静止的最短距离  x = v ** 2 / (2 * a)
        MSD_x = (ego["speed_x"] ** 2) / (
            2 * self._psd_max_dece * math.sin(ego["traj_heading"][k])
        )
        MSD_y = (ego["speed_y"] ** 2) / (
            2 * self._psd_max_dece * math.cos(ego["traj_heading"][k])
        )
        if RD_x < MSD_x or RD_y < MSD_y:
            return True
        return False

    def _build_v2v_event(self, ego: dict, other: dict, k: int) -> tuple:
        # 首先根据碰撞角度计算碰撞类型，追尾、前向、侧向碰撞
        theta = math.atan(ego["width"] / ego["length"])
        radian_between = abs(ego["traj_heading"][k] - other["traj_heading"][k])
        # 将两车的车头角度差转化到0-pi之间
        if radian_between > math.pi:
            radian_between = 2 * math.pi - radian_between
        ct = CollisionType.SideConflict
        if radian_between < theta:
            ct = CollisionType.RearEndConflict
        elif radian_between > math.pi - theta:
            ct = CollisionType.ForwardConflict
        cur_sec_mark = (ego["timeStamp"][-1] * 1000) % utils.MaxSecMark
        et = EventType.Vehicle
        ego_size = {"length": ego["length"], "width": ego["width"]}
        other_size = {"length": other["length"], "width": other["width"]}
        info_for_show, info_for_cwm = self._message_generate(
            cur_sec_mark, et, ct, ego, other, ego_size, other_size
        )
        return info_for_cwm, info_for_show

    def _build_v2vptc_event(self, motor: dict, vptc: dict, k: int) -> tuple:
        # 首先根据碰撞角度计算碰撞类型，追尾、前向、侧向碰撞
        # 矩形对角线与中线的夹脚
        theta = math.atan(motor["width"] / motor["length"])
        # 圆心与矩形中心的夹脚
        radian_between = utils.points_heading(
            motor["traj_point"][k], vptc["traj_point"][k]
        )
        # 将radian_between角度差转化到0-pi之间
        if radian_between > math.pi:
            radian_between = 2 * math.pi - radian_between
        if radian_between - motor["traj_heading"][k] < theta:
            ct = CollisionType.ForwardConflict
        elif radian_between - motor["traj_heading"][k] > math.pi - theta:
            ct = CollisionType.RearEndConflict
        else:
            ct = CollisionType.SideConflict
        cur_sec_mark = (motor["timeStamp"][-1] * 1000) % utils.MaxSecMark
        et = EventType.VulnerableTrafficParticipant
        motor_size = {"length": motor["length"], "width": motor["width"]}
        vptc_size = {"radius": vptc["radius"]}
        info_for_show, info_for_cwm = self._message_generate(
            cur_sec_mark, et, ct, motor, vptc, motor_size, vptc_size
        )
        return info_for_cwm, info_for_show

    def _calc_speed_and_acc(self, kinematics: dict) -> None:
        x = kinematics["x"]
        y = kinematics["y"]
        heading = kinematics["heading"]
        timeStamp = kinematics["timeStamp"]

        # 运用差分公式计算历史轨迹的线速度、线加速度以及角速度，d表示导数
        xd = utils.differentiate(x, timeStamp)
        xdd = utils.differentiate(xd, timeStamp)
        yd = utils.differentiate(y, timeStamp)
        ydd = utils.differentiate(yd, timeStamp)
        hd = utils.differentiate(heading, timeStamp)

        # 基于历史轨迹的信息，计算均值作为估计的未来运动学信息
        kinematics["speed_x"] = utils.mean(xd)
        kinematics["speed_y"] = utils.mean(yd)
        kinematics["speed"] = np.linalg.norm(  # type: ignore
            [kinematics["speed_x"], kinematics["speed_y"]]
        ).tolist()
        kinematics["acc_x"] = utils.mean(xdd)
        kinematics["acc_y"] = utils.mean(ydd)
        kinematics["angular_speed"] = utils.mean(hd)

    def _calc_traj_point(self, kinematics: dict) -> None:
        # 基于类的输入参数中的模型选择结果，运用不同模型计算未来轨迹
        if kinematics["angular_speed"] >= self._angular_speed_threshold:
            if (
                math.sqrt(kinematics["acc_x"] ** 2 + kinematics["acc_y"] ** 2)
                >= self._acc_threshold
            ):
                self._traj_predict_model = TrajectoryPredictModel.CTRA
            else:
                self._traj_predict_model = TrajectoryPredictModel.CTRV
        elif (
            math.sqrt(kinematics["acc_x"] ** 2 + kinematics["acc_y"] ** 2)
            >= self._acc_threshold
        ):
            self._traj_predict_model = TrajectoryPredictModel.CA
        else:
            self._traj_predict_model = TrajectoryPredictModel.CV
        getattr(
            self, "_calc_traj_point_{}".format(self._traj_predict_model.name)
        )(kinematics)

    def _calc_traj_point_CA(self, kinematics: dict) -> None:
        # 恒定加速度模型
        x = kinematics["x"][-1]
        y = kinematics["y"][-1]
        speed_x = kinematics["speed_x"]
        speed_y = kinematics["speed_y"]
        acc_x = kinematics["acc_x"]
        acc_y = kinematics["acc_y"]

        # 未来轨迹点信息为列表嵌套轨迹点元组
        kinematics["traj_point"] = [
            utils.ca_motion_point(
                (x, y),
                (speed_x, speed_y),
                (acc_x, acc_y),
                self._predict_interval * (i + 1),
            )
            for i in range(self._num_of_traj_points)
        ]

    def _calc_traj_point_CV(self, kinematics: dict) -> None:
        # 恒定速度模型
        x = kinematics["x"][-1]
        y = kinematics["y"][-1]
        speed_x = kinematics["speed_x"]
        speed_y = kinematics["speed_y"]

        # 未来轨迹点信息为列表嵌套轨迹点元组
        kinematics["traj_point"] = [
            utils.cv_motion_point(
                (x, y), (speed_x, speed_y), self._predict_interval * (i + 1)
            )
            for i in range(self._num_of_traj_points)
        ]

    def _calc_traj_point_CTRA(self, kinematics: dict) -> None:
        x = kinematics["x"][-1]
        y = kinematics["y"][-1]
        heading = kinematics["heading"][-1]
        speed_x = kinematics["speed_x"]
        speed_y = kinematics["speed_y"]
        angular_speed = kinematics["angular_speed"]
        acc_x = kinematics["acc_x"]
        acc_y = kinematics["acc_y"]
        # 未来轨迹点信息为列表嵌套轨迹点元组
        kinematics["traj_point"] = [
            utils.ctra_motion_point(
                (x, y),
                (speed_x, speed_y),
                (acc_x, acc_y),
                self._predict_interval * (i + 1),
                angular_speed,
                heading - math.pi / 2,
            )
            for i in range(self._num_of_traj_points)
        ]

    def _calc_traj_point_CTRV(self, kinematics: dict) -> None:
        x = kinematics["x"][-1]
        y = kinematics["y"][-1]
        heading = kinematics["heading"][-1]
        speed_x = kinematics["speed_x"]
        speed_y = kinematics["speed_y"]
        angular_speed = kinematics["angular_speed"]

        # 未来轨迹点信息为列表嵌套轨迹点元组
        kinematics["traj_point"] = [
            utils.ctrv_motion_point(
                (x, y),
                (speed_x, speed_y),
                self._predict_interval * (i + 1),
                angular_speed,
                heading - math.pi / 2,
            )
            for i in range(self._num_of_traj_points)
        ]

    def _calc_traj_heading(self, kinematics: dict) -> None:
        self._traj_heading_map[self._traj_predict_model](kinematics)

    def _calc_traj_heading_ctr(self, kinematics: dict) -> None:
        # 当前航向角
        h0 = kinematics["heading"][-1]
        # 转向速率
        turn_rate = kinematics["angular_speed"]
        # 未来航向角信息为列表
        kinematics["traj_heading"] = [
            utils.normalize_radians(
                h0 + (self._predict_interval * (i + 1)) * turn_rate
            )
            for i in range(self._num_of_traj_points)
        ]

    def _calc_traj_heading_nctr(self, kinematics: dict) -> None:
        # 轨迹点元组列表
        traj_point = kinematics["traj_point"]
        # 不考虑转向速率的模型，无法计算航向角，用位移向量的方向代替表示
        kinematics["traj_heading"] = [
            utils.points_heading(traj_point[i], traj_point[i + 1])
            for i in range(self._num_of_traj_points - 1)
        ]
        # 最后一个未来轨迹点无法计算位移向量方向，用上一个航向角代替
        kinematics["traj_heading"].append(kinematics["traj_heading"][-1])

    def _calc_motor_footprint(self, kinematics: dict) -> None:
        # 足迹即车辆的矩形框位置信息
        kinematics["traj_footprint"] = [
            utils.build_rectangle(
                kinematics["traj_point"][i],
                kinematics["traj_heading"][i],
                kinematics["length"],
                kinematics["width"],
            )
            for i in range(self._num_of_traj_points)
        ]

    def _is_valid(self, ego: dict, other: dict) -> bool:
        max_speed = max(
            abs(ego["speed_x"]),
            abs(ego["speed_y"]),
            abs(other["speed_x"]),
            abs(other["speed_y"]),
        )
        if max_speed < self._min_speed_for_checking:
            return False
        filter_dis = max_speed * self._predict_duration
        if any(
            [
                abs(ego["x"][-1] - other["x"][-1]) > filter_dis,
                abs(ego["y"][-1] - other["y"][-1]) > filter_dis,
            ]
        ):
            return False
        return True

    def _message_generate(
        self,
        sec_mark: float,
        event_type: Enum,
        collsion_type: Enum,
        ego_info: dict,
        other_info: dict,
        ego_size: dict,
        other_size: dict,
    ) -> tuple:

        info_for_show = {
            "collision_type": collsion_type.value,
            "ego": ego_info["guid"],
            "other": other_info["guid"],
            "ego_current_point": [ego_info["x"][-1], ego_info["y"][-1]],
            "other_current_point": [other_info["x"][-1], other_info["y"][-1]],
        }
        info_for_cwm = {
            "eventType": event_type.value,
            "collisionType": collsion_type.value,
            "secMark": int(sec_mark),
            "egoInfo": {
                "egoId": ego_info["guid"],
                "egoPos": {
                    "lat": self._current_frame[ego_info["guid"]]["lat"],
                    "lon": self._current_frame[ego_info["guid"]]["lon"],
                    "ele": self._current_frame[ego_info["guid"]]["ele"],
                },
                "heading": self._current_frame[ego_info["guid"]]["heading"],
                "size": ego_size,
                "kinematicsInfo": {
                    "speed": float(ego_info["speed"]),
                    "accelerate": float(
                        math.hypot(ego_info["acc_x"], ego_info["acc_y"])
                    ),
                    "angularSpeed": ego_info["angular_speed"],
                },
            },
            "otherInfo": {
                "otherId": other_info["guid"],
                "otherPos": {
                    "lat": self._current_frame[other_info["guid"]]["lat"],
                    "lon": self._current_frame[other_info["guid"]]["lon"],
                    "ele": self._current_frame[other_info["guid"]]["ele"],
                },
                "heading": self._current_frame[other_info["guid"]]["heading"],
                "size": other_size,
                "kinematicsInfo": {
                    "speed": float(other_info["speed"]),
                    "accelerate": float(
                        math.hypot(other_info["acc_x"], other_info["acc_y"])
                    ),
                    "angularSpeed": other_info["angular_speed"],
                },
            },
        }
        return info_for_show, info_for_cwm
