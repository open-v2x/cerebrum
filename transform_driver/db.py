"""redis config and data access functions."""

import orjson as json
from typing import Any
from typing import Callable
import zlib


class KVStore:
    """redis config and data access functions."""

    KEY_PREFIX = "v2xai.{}"
    EX = 5  # 过期时间

    def __init__(self, redis) -> None:
        """Class initialization."""
        self._redis = redis

    async def set(self, key: str, value: Any, ex: int = EX) -> Any:
        """Save data to redis."""
        return await self._redis.set(
            self.KEY_PREFIX.format(key),
            zlib.compress(json.dumps(value)),
            ex=ex,
        )

    async def get(
        self, key: str, convert: Callable = json.loads, empty: Any = dict
    ) -> Any:
        """Get data from redis."""
        ret = await self._redis.get(self.KEY_PREFIX.format(key))
        if ret is None:
            if callable(empty):
                return empty()
            return empty
        return convert(zlib.decompress(ret))

    def lock(self, key: str):
        """Redis lock."""
        return self._redis.lock(
            self.KEY_PREFIX.format(key), timeout=10, blocking_timeout=12
        )

    @property
    def redis(self):
        """Redis static method."""
        return self._redis
