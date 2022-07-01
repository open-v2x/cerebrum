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

"""General shared utilities."""

import math
import numpy as np
from pre_process_ai_algo.algo_lib import utils
import shapely.geometry as geo  # type: ignore
from transform_driver import consts

MaxSecMark = consts.MaxSecMark
HistoricalInterval = utils.HistoricalInterval
UpdateInterval = utils.UpdateInterval
# 行人的最小避让时间 s
MinAvoidanceTime = 2


def differentiate(x: list, t: list) -> list:
    """Difference-Based Derivative Calculation Method."""
    if len(x) > len(t):
        raise ValueError("length mismatched")
    if len(x) <= 1:
        raise ValueError("length of x must be greater than 1")
    return [(x[i + 1] - x[i]) / (t[i + 1] - t[i]) for i in range(len(x) - 1)]


def mean(x: list) -> float:
    """Mean calculation method."""
    if len(x) == 0:
        raise ValueError("x cannot be empty")
    return sum(x) / len(x)


def cv_motion_point(p0: tuple, v: tuple, t: float) -> tuple:
    """Trajectory calculation for constant velocity model."""
    return tuple(p0[i] + v[i] * t for i in range(len(p0)))


def ca_motion_point(p0: tuple, v: tuple, a: tuple, t: float) -> tuple:
    """Trajectory calculation for constant acceleration model."""
    return tuple(p0[i] + v[i] * t + 0.5 * a[i] * t * t for i in range(len(p0)))


def ctrv_motion_point(
    p0: tuple, v: tuple, t: float, w: float, theta: float
) -> tuple:
    """Trajectory calculation for constant turn rate and velocity model."""
    v_hypot = math.hypot(*v)
    theta_new = theta + w * t
    x = p0[0] + v_hypot / w * (math.sin(theta_new) - math.sin(theta))
    y = p0[1] + v_hypot / w * (math.cos(theta) - math.cos(theta_new))
    return x, y


def ctra_motion_point(
    p0: tuple, v: tuple, a: tuple, t: float, w: float, theta: float
) -> tuple:
    """Trajectory calculation for constant turn rate and acceleration model."""
    v_hypot = math.hypot(*v)
    a_hypot = math.hypot(*a)
    theta_new = theta + w * t
    x = (
        p0[0]
        + a_hypot / (w * w) * (math.cos(theta_new) - math.cos(theta))
        + 1
        / w
        * (
            (v_hypot + a_hypot * t) * math.sin(theta_new)
            - v_hypot * math.sin(theta)
        )
    )
    y = (
        p0[1]
        + a_hypot / (w * w) * (math.sin(theta_new) - math.sin(theta))
        - 1
        / w
        * (
            (v_hypot + a_hypot * t) * math.cos(theta_new)
            - v_hypot * math.cos(theta)
        )
    )
    return x, y


# Membership翻译为隶属度
def TTCMembership(TTC: float, ttc_threshold: float):
    """Membership calculation for time to collision."""
    if TTC > 2 * ttc_threshold:
        safety_membership = 1.0
        danger_membership = 0.0
    elif TTC > ttc_threshold:
        danger_membership = np.exp(
            -2 * ((np.log((2 * ttc_threshold - TTC) / ttc_threshold)) ** 2)
        )
        safety_membership = 1 - danger_membership
    else:
        safety_membership = 0.0
        danger_membership = 1.0
    return np.array([safety_membership, danger_membership])


def MMDMembership(MMD: float, speed: float, max_dece):
    """Membership calculation for min meeting distance."""
    max_dece_dis = speed**2 / (2 * max_dece)
    min_safe_dis = MinAvoidanceTime * max_dece_dis
    if MMD <= max_dece_dis:
        safety_membership = 0.0
        danger_membership = 1.0
    elif MMD <= min_safe_dis:
        u1 = min_safe_dis - max_dece_dis
        u2 = min_safe_dis + max_dece_dis
        safety_membership = 0.5 * (
            1 + np.sin((math.pi / u1) * (MMD - u2 / 2))  # type: ignore
        )
        danger_membership = 0.5 * (  # type: ignore
            1 - np.sin((math.pi / u1) * (MMD - u2 / 2))
        )
    else:
        safety_membership = 1.0
        danger_membership = 0.0
    return np.array([safety_membership, danger_membership])


def MMSMembership(MMS: float, speed: float):
    """Membership calculation for min meeting speed."""
    min_safe_speed = -speed / MinAvoidanceTime
    if MMS <= min_safe_speed:
        safety_membership = 1.0
        danger_membership = 0.0
    elif MMS <= min_safe_speed:
        u1 = -min_safe_speed
        u2 = min_safe_speed
        safety_membership = 0.5 * (
            1 + np.sin((math.pi / u1) * (MMS - u2 / 2))  # type: ignore
        )
        danger_membership = 0.5 * (  # type: ignore
            1 - np.sin((math.pi / u1) * (MMS - u2 / 2))
        )
    else:
        safety_membership = 0.0
        danger_membership = 1.0
    return np.array([safety_membership, danger_membership])


def normalize_radians(r0: float) -> float:
    """Normalize heading between 0 - 2 pi."""
    return r0 % (math.pi * 2)


def points_heading(p0: tuple, p1: tuple) -> float:
    """Heading calculation by two points."""
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    theta = math.pi / 2 - math.atan2(dy, dx)
    if theta < 0:
        return theta + 2 * math.pi
    else:
        return theta


def build_rectangle(
    point: tuple, heading: float, length: float, width: float
) -> tuple:
    """Calculate the corner coordinates of a rectangle at any angle."""
    x = point[0]
    y = point[1]

    x0 = x - 0.5 * width
    y0 = y + 0.5 * length

    x1 = x + 0.5 * width
    y1 = y0

    x2 = x1
    y2 = y - 0.5 * length

    x3 = x0
    y3 = y2

    x0, y0 = rotation(x0 - x, y0 - y, heading)
    x1, y1 = rotation(x1 - x, y1 - y, heading)
    x2, y2 = rotation(x2 - x, y2 - y, heading)
    x3, y3 = rotation(x3 - x, y3 - y, heading)

    x0 = x0 + x
    x1 = x1 + x
    x2 = x2 + x
    x3 = x3 + x
    y0 = y0 + y
    y1 = y1 + y
    y2 = y2 + y
    y3 = y3 + y

    return (x0, y0), (x1, y1), (x2, y2), (x3, y3)


def rotation(x: float, y: float, theta: float) -> tuple:
    """Rotation function between coordinate systems."""
    cos = math.cos(theta)
    sin = math.sin(theta)
    return x * cos - y * sin, x * sin + y * cos


def is_rects_overlapped(rect0: tuple, rect1: tuple) -> bool:
    """Determine if two rectangles overlap."""
    rect0_geo = geo.Polygon(rect0)
    rect1_geo = geo.Polygon(rect1)
    return rect0_geo.intersects(rect1_geo)


def is_rect_and_circle_overlapped(
    rect: tuple, point: tuple, radius: float
) -> bool:
    """Determine if rectangle and circle overlap."""
    rect_geo = geo.Polygon(rect)
    point_buffer = geo.Point(point).buffer(radius)
    return point_buffer.intersects(rect_geo)
