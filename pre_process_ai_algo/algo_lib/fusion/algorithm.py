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

"""Algorithms required for fusion.

1. Kalman filter algorithm
2. Hungarian matching algorithm

"""

import cv2  # type: ignore
import numpy as np


class KalmanFilter:
    """Apply kalman fitting for data fusion.

    Structural logic:
    1. Determine whether the data length meets the kalman filtering
    2. Expand the sample up to 50 for trajectories for accuracy if length over
       20 else, return polyfit result
    3. after sample expansion, apply kalman filter for x and y respectively
    4. return filtered data

    """

    Frequency = 30  # 扩样频率

    def run(self, x, y, t):
        """Class initialization.

        Input:
        x : np.array
            The x-coordinate point vector of the trajectory
            in the geodetic coordinate system. The unit is m.
        y : np.array
            The y-coordinate point vector of the trajectory
            in the geodetic coordinate system. The unit is m.
        t : np.array
            The time series vector of the trajectory. The unit is second.

        Output:
        x : np.array
            The x-coordinate point vector after fusion
            in the geodetic coordinate system. The unit is m.
        y : np.array
            The y-coordinate point vector after fusion
            in the geodetic coordinate system. The unit is m.
        t : np.array
            The time series vector after fusion. The unit is second.

        """
        time_squence = len(t)
        fit_x = np.polyfit(t, x, 1)  # 对横坐标的fit
        fit_y = np.polyfit(t, y, 1)  # 对横坐标的fit
        p1, p2 = np.poly1d(fit_x), np.poly1d(fit_y)
        if time_squence > 5:
            # 1s数据涵盖充足运动信息，10个点节省历史数据数量
            # 插值50为保证kalman迭代高频取点精度
            time_line = np.linspace(
                t[0], t[time_squence - 1], int(self.Frequency)
            )
            x, y = p1(time_line), p2(time_line)
            [xp, yp] = self._kalman_pre(x, y, time_line)
        else:
            time_line = np.linspace(t[0], t[time_squence - 1], time_squence)
            xp, yp = p1(time_line), p2(time_line)
        return [xp, yp, time_line]

    def _kalman_pre(self, x, y, t):
        # 参数初始化
        n_iter = len(x)
        x = x.astype(np.float32)
        y = y.astype(np.float32)
        t = t.astype(np.float32)
        kalman = cv2.KalmanFilter(4, 2)
        dt = (t[-1] - t[-2]) * 1e-3
        kalman.measurementMatrix = np.array(
            [[1, 0, 0, 0], [0, 1, 0, 0]], np.float32
        )
        kalman.transitionMatrix = np.array(
            [[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]],
            np.float32,
        )
        kalman.processNoiseCov = (
            np.array(
                [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
                np.float32,
            )
            * 1e-2
        )
        kalman.measurementNoiseCov = (
            np.array([[1, 0], [0, 1]], np.float32) * 0.01
        )
        xp, yp = np.array([]), np.array([])
        for k in range(n_iter):
            mes = np.reshape([x[k], y[k]], (2, 1))
            kalman.correct(mes)
            pre = kalman.predict()
            cpx, cpy = pre[0], pre[1]
            xp, yp = np.hstack((xp, cpx)), np.hstack((yp, cpy))
        return xp, yp


class Hungarian:
    """Hungarian matching algorithm."""

    def _search_extend_path(
        self, l_node, adjoin_map, l_match, r_match, visited_set
    ):
        # 邻接节点
        for r_node in adjoin_map[l_node]:
            # 情况1： 未匹配, 则找到增广路径，取反
            if r_node not in r_match:
                l_match[l_node] = r_node
                r_match[r_node] = l_node
                return True
            # 情况2：　已匹配
            next_l_node = r_match[r_node]
            if next_l_node not in visited_set:
                visited_set.add(next_l_node)
                # 找到增广路径，取反
                if self._search_extend_path(
                    next_l_node, adjoin_map, l_match, r_match, visited_set
                ):
                    l_match[l_node] = r_node
                    r_match[r_node] = l_node
                    return True
                return False

    def run(self, adjoin_map):
        """External call function.

        Input:
        adjoin_map : DICTIONARY
            {x_i: [y_j, y_k], x_j: [y_k]}

        Output:
        l_match : DICTIONAY
            RETURN THE MAX MATCHING PAIRS
            {x_i: y_j, x_j: y_k}

        Case
        ----
        from Hungarian import Hungarian as HU
        aa={1: [2, 3], 2:[2], 3:[1]}
        match=HU()
        print(match.run(aa))

        """
        # 存放匹配
        l_match, r_match = {}, {}
        for lNode in adjoin_map:
            self._search_extend_path(
                lNode, adjoin_map, l_match, r_match, set()
            )
        return l_match
