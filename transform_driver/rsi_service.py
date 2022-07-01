"""Message forwarder."""

import orjson as json
from transform_driver import consts


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
