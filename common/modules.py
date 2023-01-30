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
from config import devel as config

# from functools import reduce
import importlib
import os
import yaml

algorithm_topo = {
    "rsi_formatter": ["rsi_formatter"],
    "pre_process_ai_algo": ["complement", "fusion", "smooth"],
    "scenario_algo": [
        "collision_warning",
        "cooperative_lane_change",
        "do_not_pass_warning",
        "sensor_data_sharing",
        "reverse_driving_warning",
        "congestion_warning",
    ],
    "post_process_algo": ["post_process"],
}

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
        "post_process",
    ],
)


def load_algorithm_modules(config) -> None:
    """Load algorithm modules."""
    algos = yaml.safe_load(config.DEFAULT_ALGORITHM_YAML)

    algo_yaml = config.algorithm_yaml
    if os.path.exists(config.algorithm_yaml):
        with open(algo_yaml) as f:
            algos = yaml.safe_load(f)

    # algorithms.
    # TODO(wu.wenxiang) Add try exception to show which prefix/module error
    for prefix, modules in algorithm_topo.items():
        for m in modules:
            algo = namedtuple(m, ["module", "algo", "enable"])  # type: ignore
            algo.module = importlib.import_module(  # type: ignore
                algos[prefix]["algos"][m]["module"]
            )
            algo.algo = algos[prefix]["algos"][m]["algo"]  # type: ignore
            algo.enable = algos[prefix]["algos"][m]["enable"]  # type: ignore
            setattr(algorithms, m, algo)


load_algorithm_modules(config)
