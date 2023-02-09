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

"""Call the millimeter wave radara lgorithm function."""
from common import consts
from common import modules
import json
from common.log import Loggings

millimeter_wave_radar = None
# fusion = modules.algorithms.fusion.module

logger = Loggings()


class RadarServer:
    """Call the millimeter wave radara lgorithm function.

    1. Call the millimeter wave radara lgorithm function.

    """

    def __init__(self, mqtt, kv, mqtt_conn=None, node_id=None) -> None:
        """Class initialization."""
        self._mqtt = mqtt
        self.node_id = node_id
        self._exe = millimeter_wave_radar

    async def run(
        self, rsu: str, data: dict, rsu_id: int, _: dict = {}
    ) -> dict:  # type: ignore
        """External call function."""
        # ret= self._exe.run()
        ret = data  # type: ignore
        if self._mqtt:
            self._mqtt.publish(
                consts.RADAR_VISUAL_TOPIC.format(rsu), json.dumps(ret), 0
            )
        return ret
