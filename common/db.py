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
import yaml

import collections
from common import consts
from common.log import Loggings
from config import devel as cfg
from copy import deepcopy
from datetime import datetime
import orjson as json  # type: ignore
from sqlalchemy import Column, ForeignKey  # type: ignore
from sqlalchemy import create_engine  # type: ignore
from sqlalchemy import DateTime  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import deferred  # type: ignore
from sqlalchemy import Float, Boolean  # type: ignore
from sqlalchemy import Integer  # type: ignore
from sqlalchemy import JSON  # type: ignore
from sqlalchemy.orm import sessionmaker, relationship  # type: ignore
from sqlalchemy import String  # type: ignore
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
import zlib

logger = Loggings()
rsu_info: Dict[str, dict] = {}
lane_info: Dict[str, dict] = {}
map_info: Dict[str, dict] = {}
intersection_info: Dict[str, dict] = {}
speed_limits: Dict[str, dict] = {}
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


class DandelionBase:  # type: ignore
    """Basic class."""

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    create_time = Column(
        DateTime, nullable=False, default=lambda: datetime.utcnow()
    )
    update_time = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )


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
    intersection_code = Column(String(64), ForeignKey("intersection.code"))


class MQTT(Base):  # type: ignore
    """Define the MQTT object."""

    __tablename__ = "system_config"
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, nullable=True, default=0)
    mqtt_config = Column(JSON, nullable=True)


class EdgeNodeRSU(Base, DandelionBase):  # type: ignore
    """EdgeNodeRSU."""

    __tablename__ = "edge_node_rsu"

    edge_node_id = Column(Integer, ForeignKey("edge_node.id"))
    intersection_code = Column(String(64), ForeignKey("intersection.code"))
    name = Column(String(64), nullable=False, index=True)
    esn = Column(String(64), nullable=False, index=True)
    location = Column(JSON, nullable=False)
    edge_rsu_id = Column(Integer, nullable=False)

    def to_all_dict(self):
        """To all dict."""
        return dict(
            id=self.id,
            name=self.name,
            esn=self.esn,
            location=self.location,
            createTime=self.create_time,
            edge_rsu_id=self.edge_rsu_id,
        )

    def __repr__(self) -> str:
        """repr."""
        return f"<EdgeNodeRSU(name='{self.name}', esn='{self.esn}')>"


class Optional(object):  # type: ignore
    """Optional."""

    def __init__(self, val):
        """Init."""
        self.val = val

    @staticmethod
    def none(val):
        """none."""
        return Optional(val)

    def map(self, func):
        """map."""
        if self.val is None:
            return self
        self.val = func(self.val)
        return self

    def get(self):
        """get."""
        return self.val

    def orElse(self, val_):
        """orElse."""
        if self.val is None:
            return val_
        return self.get()


class Map(Base, DandelionBase):  # type: ignore
    """Map."""

    __tablename__ = "map"

    name = Column(String(64), nullable=False, index=True, unique=True)
    intersection_code = Column(
        String(64), ForeignKey("intersection.code")
    )  # type: ignore
    desc = Column(String(255), nullable=False, default="")
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    data = deferred(Column(JSON, nullable=True))
    bitmap_filename = Column(String(64), nullable=True)

    def __repr__(self) -> str:
        """Repr."""
        return f"<Map(name='{self.name}')>"

    def to_dict(self):
        """To dict."""
        return {
            **dict(
                id=self.id,
                intersection_code=self.intersection_code,
                name=self.name,
                desc=self.desc,
                amount=len(self.rsus),
                lat=self.lat,
                lng=self.lng,
                createTime=self.create_time,
            ),
            **Optional.none(self.intersection)
            .map(lambda v: v.to_all())
            .orElse({}),
        }


if cfg.db_server == "sqlite":
    sqlite()


class Intersection(Base, DandelionBase):  # type: ignore
    """Intersection."""

    __tablename__ = "intersection"

    code = Column(String(64), unique=True, index=True, nullable=False)

    def __repr__(self) -> str:
        """repr."""
        return f"<Intersection(code='{self.code}', name='{self.name}')>"

    def to_dict(self):
        """to_dict."""
        return dict(
            id=self.id,
            code=self.code,
            name=self.name,
            lng=self.lng,
            lat=self.lat,
            **self.to_area(),
        )


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
            RSU.intersection_code,
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
            RSU.intersection_code,
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
                "intersection_code": row[8],
            }
        except Exception as e:
            logger.error(
                f"Missing required field data in RSU with serial number "
                f":{row[0]}, ERROR: {e}"
            )
    session.close()


def get_map_info():
    """Get information of all Map."""
    results = session.query(Map.name, Map.intersection_code, Map.data).all()
    for row in results:
        try:
            """
            link_dict 样例
            {
            '19-17': ['14', '15'],
            '19-18': ['20', '21', '22'],
            '18-19': ['16', '17', '18', '19'],
            '21-19': ['23', '24', '1'],
            '20-19': ['4', '5', '6', '7'],
            '17-19': ['11', '12', '13'],
            '19-20': ['8', '9', '10'],
            '19-21': ['2', '3']
            }
            """
            link_dict = {}
            # map.json 中每条车道的 +1 -1
            map_lane_info0 = {}
            # 车道线的限速标准
            lane_speed_info = {}
            for item in row[2]["nodes"]["Node"]:
                for link in item["inLinks"]["Link"]:
                    lane_list = []

                    if "speedLimits" in link:
                        regulatory_speed_limits = link["speedLimits"][
                            "RegulatorySpeedLimit"
                        ]
                        if not isinstance(regulatory_speed_limits, list):
                            regulatory_speed_limits = [regulatory_speed_limits]

                        speed_limits_info = {
                            list(i["type"].keys())[0]: int(i["speed"])
                            for i in regulatory_speed_limits
                        }
                        for lane in link["lanes"]["Lane"]:
                            lane_speed_info[
                                int(lane["laneID"])
                            ] = speed_limits_info
                    else:
                        for lane in link["lanes"]["Lane"]:
                            lane_speed_info[int(lane["laneID"])] = {
                                "vehicleMaxSpeed": None,
                                "vehicleMinSpeed": None,
                            }

                    lane_speed = deepcopy(lane_speed_info)
                    speed_limits[row[1]] = lane_speed

                    for lane in link["lanes"]["Lane"]:
                        lane_list.append(lane["laneID"])

                    lanes = deepcopy(lane_list)
                    link_dict[link["name"]] = lanes

            key_list = [key.split("-")[-1] for key in link_dict.keys()]
            center_node = [
                item
                for item, count in collections.Counter(key_list).items()
                if count > 1
            ]

            # 取中心节点的参考经纬度
            for node in row[2]["nodes"]["Node"]:
                if node["name"] == center_node[0]:
                    del node["refPos"]["elevation"]
                    node["refPos"]["lon"] = (
                        int(node["refPos"].pop("long")) / consts.CoordinateUnit
                    )
                    node["refPos"]["lat"] = (
                        int(node["refPos"]["lat"]) / consts.CoordinateUnit
                    )
                    refPos = node["refPos"]

            # 计算车道线的+1 -1
            for num, link in enumerate(link_dict):
                if link.split("-")[-1] == center_node[0]:
                    dict0 = dict(
                        [(int(v), +1) for i, v in enumerate(link_dict[link])]
                    )
                    new_dict0 = deepcopy(dict0)
                    map_lane_info0.update(new_dict0)
                    pass
                else:
                    dict1 = dict(
                        [(int(v), -1) for i, v in enumerate(link_dict[link])]
                    )
                    new_dict1 = deepcopy(dict1)
                    map_lane_info0.update(new_dict1)
                    pass

            map_info[row[0]] = {
                "intersection_code": row[1],  # type: ignore [no-redef]
                "pos": refPos,  # type: ignore
                "lane_info": map_lane_info0,  # type: ignore
            }

        except Exception as e:
            logger.error(  # type: ignore
                "Missing required field data in Map with serial number"  # type: ignore
            )  # type: ignore

    session.close()


def get_intersection_info():
    """Get information of all Intersection."""
    results = session.query(Intersection.code).all()
    for row in results:
        try:
            intersection_info[row[0]] = {}
        except Exception as e:
            logger.error(
                f"Missing required field data in Intersection with serial number "
                f":{row[0]}, ERROR: {e}"
            )
    session.close()


def get_mqtt_config():
    """Get the configuration of mqtt."""
    try:
        # mqtt 的配置
        results = session.query(MQTT.mqtt_config, MQTT.node_id).first()
        mq_cfg = results[0]
        # RSU 与 NodeId 的对应关系
        result = session.query(EdgeNodeRSU.esn, EdgeNodeRSU.edge_node_id).all()
        rsu_nodeid: Dict = {}
        for item in result:
            rsu_nodeid[item[0]] = item[1]
        # RSU 与 路口Id 的对应关系
        res = session.query(RSU.rsu_esn, RSU.intersection_code).all()
        rsu_intersectionid: Dict = {}
        for item in res:
            rsu_intersectionid[item[0]] = item[1]

        session.close()
        return mq_cfg, rsu_nodeid, rsu_intersectionid  # type: ignore
    except Exception:
        session.close()
        logger.error(
            "unable to \
            fetch mqtt configuration from database"
        )


def put_rsu_nodeid():
    """Put the configuration of nodeid."""
    try:
        results = session.query(
            EdgeNodeRSU.esn, EdgeNodeRSU.edge_node_id
        ).all()
        rsu_nodeid: Dict = {}
        for item in results:
            rsu_nodeid[item[0]] = item[1]
        session.close()
        return rsu_nodeid  # type: ignore
    except Exception:
        session.close()
        logger.error(
            "unable to \
            fetch nodeid configuration from database"
        )


def put_rsu_intersectionid():
    """Put the configuration of intersectionid."""
    try:
        results = session.query(RSU.rsu_esn, RSU.intersection_code).all()
        rsu_intersectionid: Dict = {}
        for item in results:
            rsu_intersectionid[item[0]] = item[1]
        session.close()
        return rsu_intersectionid  # type: ignore
    except Exception:
        session.close()
        logger.error(
            "unable to \
            fetch intersectionid configuration from database"
        )
    pass


class AlgoVersion(Base):  # type: ignore
    """Define the Algo version object."""

    __tablename__ = "algo_version"

    id = Column(Integer, primary_key=True)
    algo = Column(String(64), ForeignKey("algo_name.name"))
    version = Column(String(64), nullable=False)
    version_path = Column(String(64), nullable=True)


class AlgoName(Base):  # type: ignore
    """Define the Algo object."""

    __tablename__ = "algo_name"

    id = Column(Integer, primary_key=True)
    module = Column(String(64), ForeignKey("algo_module.module"))
    name = Column(String(64), nullable=False, index=True)
    enable = Column(Boolean, nullable=False, default=False)
    module_path = Column(String(64), nullable=False)
    in_use = Column(String(64), nullable=True)
    algo_versions: List[AlgoVersion] = relationship(
        "AlgoVersion", backref="algo_name"
    )


def get_algo_config():
    """Get algo config from database."""
    algo_config_in_db = session.query(AlgoName).all()
    algo_config = yaml.safe_load(cfg.DEFAULT_ALGORITHM_YAML)
    for algo_name_in_db in algo_config_in_db:
        algo_config[algo_name_in_db.module]["algos"][algo_name_in_db.name][
            "enable"
        ] = algo_name_in_db.enable
        if algo_name_in_db.in_use:
            algo_config[algo_name_in_db.module]["algos"][algo_name_in_db.name][
                "algo"
            ] = algo_name_in_db.in_use
        algo_version_dict = {
            version.version: version.version_path
            for version in algo_name_in_db.algo_versions
        }
        algo_config[algo_name_in_db.module]["algos"][algo_name_in_db.name][
            "version"
        ].extend(algo_version_dict.keys())
        if (
            algo_name_in_db.in_use in algo_version_dict.keys()
            and algo_version_dict.get(algo_name_in_db.in_use)
        ):
            algo_config[algo_name_in_db.module]["algos"][algo_name_in_db.name][
                "module"
            ] = algo_version_dict.get(algo_name_in_db.in_use)
    return yaml.safe_dump(algo_config, sort_keys=False)


cfg.DEFAULT_ALGORITHM_YAML = get_algo_config()
