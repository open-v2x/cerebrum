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

"""Message forwarder."""

from common import consts
import orjson as json


class RSI:
    """Set rsi information in redis and send it to rsu."""

    RSI_KEY = "rsi.{}"
    CONGESTION_KEY = "congestion.{}"

    def __init__(self, mqtt, kv) -> None:
        """Class initialization."""
        self._kv = kv
        self._mqtt = mqtt

    async def run(
        self, rsu_id: str, std_rsi: dict, congestion_info: bool
    ) -> None:
        """External call function."""
        await self._kv.set(self.RSI_KEY.format(rsu_id), std_rsi)
        self._mqtt.publish(
            consts.RSI_DOWN_TOPIC.format(rsu_id), json.dumps(std_rsi), 0
        )
        self._mqtt.publish(
            consts.RSI_UP_TOPIC.format(rsu_id), json.dumps(std_rsi), 0
        )
        if congestion_info:
            await self._kv.set(
                self.CONGESTION_KEY.format(rsu_id), congestion_info
            )
