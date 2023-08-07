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
"""utils."""
from sensor_data_sharing_service import constants


def coordinate_tf(lat, lon, tf, unit=constants.COORDINATE_UNIT) -> tuple:
    """Convert latitude and longitude to geodetic coordinates."""
    return tf.transform(lat / unit, lon / unit)  # y, x


def coordinate_tf_inverse(y, x, tf, unit=constants.COORDINATE_UNIT) -> tuple:
    """Convert geodetic coordinates to latitude and longitude."""
    # 平面坐标 -->  经纬度坐标
    lat, lon = tf.transform(y, x, direction="INVERSE")
    if type(lat) == float:
        return int(lat * unit), int(lon * unit)
    return (lat * unit).astype(int), (lon * unit).astype(int)


def differentiate(x: list, t: list) -> list:
    """Difference-Based Derivative Calculation Method."""
    if len(x) > len(t):
        raise ValueError("length mismatched")
    if len(x) <= 1:
        raise ValueError("length of x must be greater than 1")
    return [(x[i + 1] - x[i]) / (t[i + 1] - t[i]) for i in range(len(x) - 1)]
