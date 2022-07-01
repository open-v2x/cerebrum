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

"""Call the smooth algorithm function."""

from pre_process_ai_algo.algo_lib import smooth
from pre_process_ai_algo.pipelines import Base


class PolynomialSmooth(Base):
    """Call the polynomial smooth algorithm function.

    1. Call the polynomial smooth algorithm function.
    2. Accessing redis data required by the polynomial smooth algorithm
       function.

    """

    HIS_INFO_KEY = "smooth.polyn.his.{}"

    def __init__(self, kv):
        """Class initialization."""
        super().__init__(kv)
        self._exe = smooth.Polynomial()


class ExponentialSmooth(Base):
    """Call the exponential smooth algorithm function.

    1. Call the exponential smooth algorithm function.
    2. Accessing redis data required by the exponential smooth algorithm
       function.

    """

    HIS_INFO_KEY = "smooth.exp.his.{}"

    def __init__(self, kv):
        """Class initialization."""
        super().__init__(kv)
        self._exe = smooth.Exponential()
