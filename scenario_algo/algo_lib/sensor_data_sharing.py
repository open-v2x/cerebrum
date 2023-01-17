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

"""Scenario of Sensor Data Sharing."""

import numpy as np
from post_process_algo import post_process
from pre_process_ai_algo.algo_lib.utils import MaxSecMark
from scenario_algo.algo_lib import utils
import shapely.geometry as geo  # type: ignore
import time
from typing import List


class Base:
    """Super class of SensorDataSharing class."""

    def run(
        self,
        motor_kinematics: dict,
        vptc_kinematics: dict,
        rsi: dict,
        msg_VIR: dict,
        sensor_pos: dict,
        transform_info: list,
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class SensorDataSharing(Base):
    """Scenario of Sensor Data Sharing.

    Structural logic:
    1. Calculate the future trajectory of the requested vehicle based on its
       latitude and longitude and the expected trajectory
    2. Build buffers for future trajectories
    3. Look for interacting vehicles and vulnerable traffic participants in
       buffer zones
    4. Obtain basic information and historical and future trajectory
       information of interactive targets
    5. Based on rsi, get the obstacle information near the requested vehicle
    6. Generate msg_SSM based on participant information and obstacle
       information

    """

    def __init__(self) -> None:
        """Class initialization."""
        self._polynomial_degree = 2
        self._future_traj_point_num = 30
        self._path_radius = 10
        self._min_dis = 0.3

    def run(
        self,
        motor_kinematics: dict,
        vptc_kinematics: dict,
        rsi: dict,
        msg_VIR: dict,
        sensor_pos: dict,
        transform_info: list,
    ) -> tuple:
        """External call function.

        Input:
        motor_kinematics : dict
        motors' kinematics information

        vptc_kinematics : dict
        vulnerable participants' kinematics information

        msg_VIR : dict
        It is vehicle's lane-changing requirements from OBU

        transform_info:
        Information required for the conversion of latitude and longitude to
        the geodetic coordinate system

        sensor_pos:
        RSU postion required for generating msg_SSM

        Output:
        msg_SSM : dict

        info_for_show : dict
        information for visualization

        """
        self._speed_threshold = 2.8
        self._transform_info = transform_info
        self._transformer = self._transform_info[0]
        self._msg_SSM = {
            "msgCnt": int(msg_VIR["msgCnt"]),
            "id": msg_VIR["intAndReq"]["reqs"]["targetRSU"],
            "equipmentType": 1,
            "sensorPos": sensor_pos,
            "secMark": int(time.time() * 1000 % MaxSecMark),
            "egoPos": msg_VIR["refPos"],
            "egoId": msg_VIR["id"],
            "participants": [],
            "obstacles": [],
        }
        self._add_participants(msg_VIR, motor_kinematics, vptc_kinematics)
        self._add_obstacles(rsi)
        self._time_stamp = int(time.time() * 1000)

        return self._msg_SSM, self._info_for_show

    def _add_participants(
        self, msg_VIR: dict, motor_kinematics: dict, vptc_kinematics: dict
    ):
        self.ego_y, self.ego_x = post_process.coordinate_tf(
            msg_VIR["refPos"]["lat"],
            msg_VIR["refPos"]["lon"],
            self._transformer,
        )
        traj_buffer = self._build_traj_buffer(msg_VIR)
        motor_list, motor_show = self._filter_motor(
            motor_kinematics, traj_buffer
        )
        vptc_list, vptc_show = self._filter_vptc(vptc_kinematics, traj_buffer)
        self._msg_SSM["participants"] = motor_list + vptc_list

        self._generate_show_data(motor_show + vptc_show)

    def _generate_show_data(self, other_info: list):
        self._info_for_show = {
            "type": "SDS",
            "ego_point": {
                "x": self.ego_x - self._transform_info[1],
                "y": self.ego_y - self._transform_info[2],
            },
            "other_cars": other_info,
        }

    def _add_obstacles(self, rsi: dict):
        if len(rsi):
            obstacle_list = self._build_obstacle_info(rsi)
            self._msg_SSM["obstacles"] = obstacle_list

    def _build_traj_buffer(self, msg_VIR: dict):
        requested_traj = msg_VIR["intAndReq"]["reqs"]["info"]["sensorSharing"][
            "detectArea"
        ]["activePath"]
        points_num = len(requested_traj)
        his_t = np.zeros(points_num)
        his_lon = np.zeros(points_num)
        his_lat = np.zeros(points_num)
        for i, traj in enumerate(requested_traj):
            his_t[i] = i
            his_lon[i], his_lat[i] = traj["lon"], traj["lat"]
        his_y, his_x = post_process.coordinate_tf(
            his_lat, his_lon, self._transformer
        )
        his_x -= self._transform_info[1]
        his_y -= self._transform_info[2]
        if self._is_speed_enough(his_x, his_y, his_t):
            x_fit = np.polyfit(  # type: ignore
                his_t, his_x, self._polynomial_degree
            )
            y_fit = np.polyfit(  # type: ignore
                his_t, his_y, self._polynomial_degree
            )
            time_list = np.array(
                [i + points_num for i in range(self._future_traj_point_num)]
            )
            x = np.polyval(x_fit, time_list)  # type: ignore
            y = np.polyval(y_fit, time_list)  # type: ignore
            predicted_x = np.concatenate((his_x, x), axis=0)
            predicted_y = np.concatenate((his_y, y), axis=0)
            traj_line = geo.LineString(list(zip(predicted_x, predicted_y)))
            return traj_line.buffer(self._path_radius)
        return geo.Point(
            [
                self.ego_x - self._transform_info[1],
                self.ego_y - self._transform_info[2],
            ]
        ).buffer(2 * self._path_radius)

    def _filter_motor(self, motor_kinematics: dict, traj_buffer) -> tuple:
        motor_list = []
        show_list = []
        for obj_id, obj_info in motor_kinematics.items():
            obj_point = geo.Point(obj_info["x"][-1], obj_info["y"][-1])
            if (
                traj_buffer.intersects(obj_point)
                and abs(
                    self.ego_x - self._transform_info[1] - obj_info["x"][-1]
                )
                > self._min_dis
                and abs(
                    self.ego_y - self._transform_info[2] - obj_info["y"][-1]
                )
                > self._min_dis
            ):
                show_list.append(
                    {
                        "x": obj_info["x"][-1],
                        "y": obj_info["y"][-1],
                    }
                )
                motor_list.append(self._build_motor_info(obj_info))
        return motor_list, show_list

    def _filter_vptc(self, vptc_kinematics: dict, traj_buffer) -> tuple:
        vptc_list = []
        show_list = []
        for obj_id, obj_info in vptc_kinematics.items():
            obj_point = geo.Point(obj_info["x"][-1], obj_info["y"][-1])
            if (
                traj_buffer.intersects(obj_point)
                and abs(
                    self.ego_x - self._transform_info[1] - obj_info["x"][-1]
                )
                > self._min_dis
                and abs(
                    self.ego_y - self._transform_info[2] - obj_info["y"][-1]
                )
                > self._min_dis
            ):
                show_list.append(
                    {
                        "x": obj_info["x"][-1],
                        "y": obj_info["y"][-1],
                    }
                )
                vptc_list.append(self._build_vptc_info(obj_info))
        return vptc_list, show_list

    def _build_vptc_info(self, obj_info: dict) -> dict:
        (
            his_x,
            his_x,
            his_lat,
            his_lon,
            predicted_lat,
            predicted_lon,
        ) = self._traj_predict(obj_info)
        vptc_info = {
            "ptcType": obj_info["ptcType"],
            "ptcHistoricalTrajectory": self._build_traj_list(his_lat, his_lon),
            "ptcPredictedTrajectory": self._build_traj_list(
                predicted_lat, predicted_lon
            ),
            "ptcTrackTimeStamp": obj_info["timeStamp"][-1],
            "ptcRadius": int(obj_info["radius"] / 0.01),
        }
        return vptc_info

    def _build_motor_info(self, obj_info: dict) -> dict:
        (
            his_x,
            his_x,
            his_lat,
            his_lon,
            predicted_lat,
            predicted_lon,
        ) = self._traj_predict(obj_info)
        motor_info = {
            "ptcType": "motor",
            "ptcHistoricalTrajectory": self._build_traj_list(his_lat, his_lon),
            "ptcPredictedTrajectory": self._build_traj_list(
                predicted_lat, predicted_lon
            ),
            "ptcTrackTimeStamp": self._time_stamp,
            "ptcSize": {
                "width": int(obj_info["width"] / 0.01),
                "length": int(obj_info["length"] / 0.01),
                "height": int(obj_info["height"] / 0.05),
            },
            "ptcHeading": int(obj_info["heading"][-1] / 0.0125),
            "ptcAngleSpeed": int(obj_info["angular_speed"] / 0.02),
        }
        return motor_info

    def _traj_predict(self, obj_info: dict) -> tuple:
        his_x = np.array(obj_info["x"]) + self._transform_info[1]
        his_y = np.array(obj_info["y"]) + self._transform_info[2]
        his_lat, his_lon = post_process.coordinate_tf_inverse(
            his_y, his_x, self._transformer
        )
        predicted_traj = np.array(obj_info["traj_point"])
        predicted_x = predicted_traj[:, 0]
        predicted_y = predicted_traj[:, 1]
        predicted_lat, predicted_lon = post_process.coordinate_tf_inverse(
            predicted_y + self._transform_info[2],
            predicted_x + self._transform_info[1],
            self._transformer,
        )
        return his_x, his_x, his_lat, his_lon, predicted_lat, predicted_lon

    def _build_obstacle_info(self, rsi: dict) -> list:
        obstacle_list: List = []

        if not rsi.get("content"):
            return obstacle_list

        for event_info in rsi["content"]["rsiDatas"][0]["rtes"]:
            if event_info["eventType"] in [401, 406]:  # ThrowingObject Animal
                obstacle_list.append(
                    {
                        "obstacleType": event_info["eventType"],
                        "source": event_info["eventSource"],
                    }
                )
        return obstacle_list

    def _build_traj_list(self, lat, lon) -> list:
        traj_list = []
        for i in range(len(lat)):
            traj_dict = {}
            traj_dict["lat"], traj_dict["lon"] = int(lat[i]), int(lon[i])
            traj_list.append(traj_dict)
        return traj_list

    def _is_speed_enough(self, x, y, t) -> bool:
        xd = utils.differentiate(x, t / 1000)
        yd = utils.differentiate(y, t / 1000)
        if max(max(xd), max(yd)) > self._speed_threshold:
            return True
        return False
