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
import importlib
import os
import yaml

algorithms = namedtuple(
    "algorithms",
    [
        "rsi_formatter",
        "pre_process_complement",
        "pre_process_fusion",
        "pre_process_smooth",
    ],
)


def load_algorithm_modules(config) -> None:
    """Load algorithm modules."""
    algos = yaml.safe_load(config.DEFAULT_ALGORITHM_YAML)

    algo_yaml = config.algorithm_yaml
    if os.path.exists(config.algorithm_yaml):
        with open(algo_yaml) as f:
            algos = yaml.safe_load(f)

    algorithms.rsi_formatter = importlib.import_module(
        algos["rsi_formatter"]["algo"]
    )
    algorithms.pre_process_complement = importlib.import_module(
        algos["pre_process_ai_algo"]["algos"]["complement"]["algo"]
    )
    algorithms.pre_process_fusion = importlib.import_module(
        algos["pre_process_ai_algo"]["algos"]["fusion"]["algo"]
    )
    algorithms.pre_process_smooth = importlib.import_module(
        algos["pre_process_ai_algo"]["algos"]["smooth"]["algo"]
    )


load_algorithm_modules(config)
