"""Smooth Algorithm.

1. Exponential Smooth
2. Polynomial Smooth

"""

import numpy as np
from pre_process_ai_algo.algo_lib import utils


class Base:
    """Super class of Exponential class and Polynomial class."""

    def run(
        self, context_frames: dict, current_frame: dict, last_timestamp: int
    ) -> tuple:
        """External call function."""
        raise NotImplementedError


class Exponential(Base):
    """Exponential Smooth Algorithm.

    Structural logic:
    1. Combine historical frame data and current frame data
    2. Find the trajectory of the participant's previous frame
    3. Smooth the latest trajectory point by exponential smooth function

    """

    def __init__(
        self, smooth_index: float = 0.8, smooth_threshold: float = 2 * 1000
    ) -> None:
        """Class initialization.

        smooth_index:
        The parameter of the smoothing formula

        smooth_threshold:
        Time threshold of trajectory points that can be used for smoothing

        """
        self._smooth_threshold = smooth_threshold
        # The parameter of the smoothing formula
        self._smooth_index = smooth_index

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
        updated_latest_frame:
        The latest frame data after smooth processing, AID format

        last_timestamp:
        Timestamp of current frame data for the next call

        """
        # 将历史数据与最新帧数据合并
        latest_id_set, last_timestamp = utils.frames_combination(
            context_frames, current_frame, last_timestamp
        )
        for obj_info in context_frames.values():
            self._smooth_one(obj_info, latest_id_set)
        return (
            utils.get_current_frame(context_frames, last_timestamp),
            last_timestamp,
        )

    def _smooth_one(self, obj_info: list, latest_id_set: set) -> list:
        try:
            current = obj_info[-1]
        except IndexError:
            return obj_info
        if any(
            [
                obj_info[-1]["global_track_id"] not in latest_id_set,
                len(obj_info) == 1,
            ]
        ):
            return obj_info
        last = obj_info[-2]
        delta_time = current["timeStamp"] - last["timeStamp"]
        if delta_time > self._smooth_threshold:
            return obj_info
        for j in ("x", "y"):
            current[j] = current[j] * self._smooth_index + last[j] * (
                1 - self._smooth_index
            )
        return obj_info


class Polynomial(Base):
    """Polynomial Smooth Algorithm.

    Structural logic:
    1. Combine historical frame data and current frame data
    2. Find the trajectory of the participant's previous frame
    3. Fit historical trajectories with polynomials
    3. Replacing the trajectory points with the result of the polynomial fit

    """

    def __init__(
        self, polynomial_degree: int = 3, points_num: int = 5
    ) -> None:
        """Class initialization.

        polynomial_degree:
        Power of polynomial

        points_num:
        The number of trajectory points involved in fitting

        """
        self.polynomial_degree = polynomial_degree
        self.points_num = points_num

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
        updated_latest_frame:
        The latest frame data after smooth processing, AID format

        last_timestamp:
        Timestamp of current frame data for the next call

        """
        # 将历史数据与最新帧数据合并
        latest_id_set, last_timestamp = utils.frames_combination(
            context_frames, current_frame, last_timestamp
        )
        for obj_info in context_frames.values():
            self._smooth_one(obj_info, latest_id_set)
        return (
            utils.get_current_frame(context_frames, last_timestamp),
            last_timestamp,
        )

    def _smooth_one(self, obj_info: list, latest_id_set: set) -> list:
        # 至少需要POINT_NUM帧数据
        if len(obj_info) < self.points_num:
            return obj_info
        if obj_info[-1]["global_track_id"] in latest_id_set:
            return obj_info
        # 把secmark，x，y列出来，
        track_t = np.zeros(self.points_num)
        track_x = np.zeros(self.points_num)
        track_y = np.zeros(self.points_num)
        for i, fr in enumerate(obj_info[-self.points_num :]):
            track_t[i], track_x[i], track_y[i] = (
                fr["timeStamp"],
                fr["x"],
                fr["y"],
            )
        # 分别对横纵坐标的历史数据进行多项式拟合
        fit = np.polyfit(  # type: ignore
            track_t, track_x, self.polynomial_degree
        )
        obj_info[-1]["x"] = float(np.polyval(fit, track_t[-1]))  # type: ignore
        fit = np.polyfit(  # type: ignore
            track_t, track_y, self.polynomial_degree
        )
        obj_info[-1]["y"] = float(np.polyval(fit, track_t[-1]))  # type: ignore
        return obj_info
