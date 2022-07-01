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
