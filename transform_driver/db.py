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

"""database config and data access functions."""

from config import devel as cfg
import orjson as json
from post_process_algo import post_process
import pymysql  # type: ignore
from transform_driver.log import Loggings
from typing import Any
from typing import Callable
from typing import Dict
import zlib

logger = Loggings()


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


rsu_info: Dict[str, dict] = {}
lane_info: Dict[str, dict] = {}


def jsonloads(in_obj):
    """Transfer input object to json if it is a string."""
    if isinstance(in_obj, str):
        in_obj = json.loads(in_obj)
    return in_obj


def get_rsu_info(msg_info):
    """Get information of all rsu."""
    conn = pymysql.connect(**cfg.mysql)
    cursor = conn.cursor()

    sql = (
        "select rsu_esn,location,bias_x,bias_y,rotation,reverse,"
        "scale,lane_info from rsu"
    )

    if msg_info:
        rsu_id = json.loads(msg_info)["esn"]
        sql += f" where rsu_esn='{rsu_id}'"

    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            _pos = jsonloads(row[1])
            _lane_info = jsonloads(row[7])
            lane_info[row[0]] = {}
            for k, v in _lane_info.items():
                lane_info[row[0]][int(k)] = v
            rsu_info[row[0]] = {
                "pos": _pos,
                "bias_x": row[2],
                "bias_y": row[3],
                "rotation": row[4],
                "reverse": row[5],
                "scale": row[6],
            }
    except Exception:
        logger.error("unable to fetch data from database")
    finally:
        conn.close()
        post_process.generate_transformation_info()


def get_mqtt_config():
    """Get the configuration of mqtt."""
    conn = pymysql.connect(**cfg.mysql)
    cursor = conn.cursor()
    sql = "select mqtt_config,node_id from system_config"
    try:
        cursor.execute(sql)
        results = cursor.fetchone()
        mq_cfg = results[0]
        node_id = results[1]
    except Exception:
        logger.error("unable to fetch mqtt configuration from database")
    finally:
        conn.close()

    mq_cfg = json.loads(mq_cfg)
    return mq_cfg, node_id
