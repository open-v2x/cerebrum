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

"""Load dynamic modules."""

from collections import namedtuple
from common.db import get_algo_from_api
import importlib


algorithms = namedtuple(  # type: ignore
    "algorithms",
    # TODO(wu.wenxiang) YAML verification to avoid dup & mis-match
    # reduce(lambda x, y: x + y, algorithm_topo.values()),
    [
        "rsi_formatter",
        "complement",
        "fusion",
        "smooth",
        "collision_warning",
        "cooperative_lane_change",
        "do_not_pass_warning",
        "sensor_data_sharing",
        "reverse_driving_warning",
        "congestion_warning",
        "overspeed_warning",
        "slowspeed_warning",
        "post_process",
    ],
)


def load_algorithm_modules() -> None:
    """Load algorithm modules."""
    algo_data = get_algo_from_api()
    for algo in algo_data:
        algo_t = namedtuple(  # type: ignore
            str(algo.get("algo")),
            ["module", "algo", "enable", "external_bool", "endpoint_config"],
        )
        algo_t.module = importlib.import_module(algo.get("modulePath"))  # type: ignore
        algo_t.algo = algo.get("inUse")  # type: ignore
        algo_t.enable = algo.get("enable")  # type: ignore
        algo_t.external_bool = algo.get("externalBool")  # type: ignore
        algo_t.endpoint_config = algo.get("endpointConfig")  # type: ignore
        setattr(algorithms, algo.get("algo"), algo_t)


load_algorithm_modules()
