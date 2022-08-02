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
from sqlalchemy import Column  # type: ignore
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy.orm import sessionmaker  # type: ignore
from sqlalchemy import String
from transform_driver.log import Loggings
from typing import Any
from typing import Callable
from typing import Dict
import zlib


logger = Loggings()
rsu_info: Dict[str, dict] = {}
lane_info: Dict[str, dict] = {}
Base = declarative_base()
engine = create_engine(**cfg.sqlalchemy_w)
DBSession = sessionmaker(bind=engine)
session = DBSession()


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


def sqlite():
    """Initialize rsu data."""
    Base.metadata.create_all(engine)
    rsu = RSU(
        rsu_esn="R328328",
        location={"lon": 118.8213963998263, "lat": 31.934846637757847},
        bias_x=0.0,
        bias_y=0.0,
        rotation=0.0,
        reverse=0,
        scale=0.09,
        lane_info={
            "1": -1,
            "2": 1,
            "3": 1,
            "4": -1,
            "5": -1,
            "6": -1,
            "7": -1,
            "8": 1,
            "9": 1,
            "10": 1,
            "11": 1,
            "12": 1,
            "13": 1,
            "14": -1,
            "15": -1,
            "16": 1,
            "17": 1,
            "18": 1,
            "19": 1,
            "20": -1,
            "21": -1,
            "22": -1,
            "23": -1,
            "24": -1,
        },
    )

    session.add(rsu)
    session.commit()
    session.close()


class RSU(Base):  # type: ignore
    """Define the RSU object."""

    __tablename__ = "rsu"
    id = Column(Integer, primary_key=True)
    rsu_esn = Column(type_=String(64), nullable=False)
    location = Column(type_=JSON, nullable=False)
    bias_x = Column(type_=Float, nullable=False)
    bias_y = Column(type_=Float, nullable=False)
    rotation = Column(type_=Float, nullable=False)
    reverse = Column(type_=Integer, nullable=False)
    scale = Column(type_=Float, nullable=False)
    lane_info = Column(type_=JSON, nullable=False)


class MQTT(Base):  # type: ignore
    """Define the MQTT object."""

    __tablename__ = "system_config"
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, nullable=True, default=0)
    mqtt_config = Column(JSON, nullable=True)


if cfg.db_server == "sqlite":
    sqlite()


def get_rsu_info(msg_info):
    """Get information of all RSU."""
    if msg_info:
        rsu_id = json.loads(msg_info)["esn"]
        results = session.query(
            RSU.rsu_esn,
            RSU.location,
            RSU.bias_x,
            RSU.bias_y,
            RSU.rotation,
            RSU.reverse,
            RSU.scale,
            RSU.lane_info,
        ).filter(RSU.rsu_esn == rsu_id)
    else:
        results = session.query(
            RSU.rsu_esn,
            RSU.location,
            RSU.bias_x,
            RSU.bias_y,
            RSU.rotation,
            RSU.reverse,
            RSU.scale,
            RSU.lane_info,
        ).all()
    for row in results:
        try:
            lane_info[row[0]] = {}
            for k, v in row[7].items():
                lane_info[row[0]][int(k)] = v
            rsu_info[row[0]] = {
                "pos": row[1],
                "bias_x": row[2],
                "bias_y": row[3],
                "rotation": row[4],
                "reverse": row[5],
                "scale": row[6],
            }
        except Exception:
            logger.error(
                "Missing required field data in RSU with serial number "
                ":{} ".format(row[0])
            )
    session.commit()
    session.close()
    post_process.generate_transformation_info()


def get_mqtt_config():
    """Get the configuration of mqtt."""
    try:
        results = session.query(MQTT.mqtt_config, MQTT.node_id).first()
        mq_cfg = results[0]
        node_id = results[1]
        session.commit()
        session.close()
        return mq_cfg, node_id
    except Exception:
        session.close()
        logger.error("unable to fetch mqtt configuration from database")
