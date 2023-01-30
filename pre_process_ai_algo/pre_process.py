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

"""Algorithm pipeline processing flow."""

import yaml

from common import consts
from common import modules
import orjson as json

from config import default
from post_process_algo import post_process
from pre_process_ai_algo.pipelines.complement import Interpolation
from pre_process_ai_algo.pipelines.complement import LstmPredict
from pre_process_ai_algo.pipelines.fusion import Fusion
from pre_process_ai_algo.pipelines.smooth import ExponentialSmooth
from pre_process_ai_algo.pipelines.smooth import PolynomialSmooth
from pre_process_ai_algo.pipelines.visualization import Visualize
from scenario_algo.svc.collision_warning import CollisionWarning
from scenario_algo.svc.congestion_warning import CongestionWarning
from scenario_algo.svc.reverse_driving_warning import ReverseDriving


class DataProcessing:
    """Convert rsm data format to algorithm format data."""

    LOCK_KEY = "v2x.process.lock.{}"
    SM_CFG_KEY = "lastsm_and_cfg.{}"

    def __init__(self, mqtt, kv, mqtt_conn=None, node_id=None) -> None:
        """Class initialization."""
        self._interpolation = Interpolation(kv)
        self._fusion = Fusion(kv)
        self._exponential_smooth = ExponentialSmooth(kv)
        self._lstm_predict = LstmPredict(kv)
        self._polynomial_smooth = PolynomialSmooth(kv)
        self._collision_warning = CollisionWarning(
            kv, mqtt, mqtt_conn, node_id
        )
        self._reverse_driving_warning = ReverseDriving(
            kv, mqtt, mqtt_conn, node_id
        )
        self._congestion_warning = CongestionWarning(
            kv, mqtt, mqtt_conn, node_id
        )
        self._visual = Visualize(kv, mqtt, mqtt_conn, node_id)
        self._kv = kv
        self._mqtt = mqtt
        self._pipelines = [
            "fusion",
            "complement",
            "smooth",
        ]
        self._nodeid_pipelines = [
            "visual",
            "collision_warning",
            "reverse_driving_warning",
            "congestion_warning"
        ]
        self._fusion_dispatch = {
            "disable": False,
            "fusion": self._fusion,
        }
        self._smooth_dispatch = {
            "disable": False,
            "exponential": self._exponential_smooth,
            "polynomial": self._polynomial_smooth,
        }
        self._complement_dispatch = {
            "disable": False,
            "interpolation": self._interpolation,
            "lstm_predict": self._lstm_predict,
        }
        self._visual_dispatch = {
            "disable": False,
            "visual": self._visual,
        }
        self._collision_warning_dispatch = {
            "disable": False,
            "collision_warning": self._collision_warning,
        }
        self._reverse_driving_warning_dispatch = {
            "disable": False,
            "reverse_driving_warning": self._reverse_driving_warning,
        }
        self._congestion_warning_dispatch = {
            "disable": False,
            "congestion_warning": self._congestion_warning,
        }

    async def run(
        self, rsu_id: str, raw_rsm: dict, miss_flag: str, miss_info: str, node_id: int
    ) -> None:
        """External call function."""
        async with self._kv.lock(self.LOCK_KEY.format(rsu_id)):
            if miss_flag == "miss_required_key":
                self._mqtt.publish(
                    consts.RSM_DAWNLINE_ACK_TOPIC.format(rsu_id), miss_info, 0
                )
                return None
            if miss_flag == "miss_optional_key":
                self._mqtt.publish(
                    consts.RSM_DAWNLINE_ACK_TOPIC.format(rsu_id), miss_info, 0
                )
            # 把 rsm 数据结构转换成算法的数据结构
            latest = post_process.rsm2frame(raw_rsm, rsu_id)
            if not latest:
                return None
            current_sec_mark = latest[list(latest.keys())[0]]["secMark"]
            sm_and_cfg = await self._kv.get(self.SM_CFG_KEY.format(rsu_id))
            last_sec_mark = sm_and_cfg["sm"] if sm_and_cfg.get("sm") else 0
            pipe_cfg = (
                # TODO(wu.wenxiang) document how to read config from mqtt
                sm_and_cfg["cfg"]
                if sm_and_cfg.get("cfg")
                else {
                    "fusion": (
                        modules.algorithms.fusion.algo
                        if modules.algorithms.fusion.enable
                        else "disable"
                    ),
                    "complement": (
                        modules.algorithms.complement.algo
                        if modules.algorithms.complement.enable
                        else "disable"
                    ),
                    "smooth": (
                        modules.algorithms.smooth.algo
                        if modules.algorithms.smooth.enable
                        else "disable"
                    ),
                    "collision_warning": (
                        modules.algorithms.collision_warning.algo
                        if modules.algorithms.collision_warning.enable
                        else "disable"
                    ),
                    "reverse_driving_warning": (
                        modules.algorithms.reverse_driving_warning.algo
                        if modules.algorithms.reverse_driving_warning.enable
                        else "disable"
                    ),
                    "congestion_warning": (
                        modules.algorithms.congestion_warning.algo
                        if modules.algorithms.congestion_warning.enable
                        else "disable"
                    ),
                    "visual": "visual",
                }
            )
            if 0 <= last_sec_mark - current_sec_mark <= 50000:
                return None
            await self._kv.set(
                self.SM_CFG_KEY.format(rsu_id),
                {"sm": current_sec_mark, "cfg": pipe_cfg},
            )
            pipelines = [
                # TODO(wu.wenxiang) check p not exist
                getattr(self, "_{}_dispatch".format(p))[pipe_cfg[p]]
                for p in self._pipelines
            ]
            for p1 in pipelines:
                if p1:
                    latest = await p1.run(rsu_id, latest)
            nodeid_pipelines = [
                # TODO(wu.wenxiang) check p not exist
                getattr(self, "_{}_dispatch".format(p))[pipe_cfg[p]]
                for p in self._nodeid_pipelines
            ]

            for p in nodeid_pipelines:
                if p:
                    latest = await p.run(rsu_id, latest, node_id)

            rsm = post_process.frame2rsm(latest, raw_rsm, rsu_id)
            self._mqtt.publish(
                consts.RSM_DOWN_TOPIC.format(rsu_id), json.dumps(rsm), 0
            )


class Cfg:
    """Receive algorithm config information and set it in redis."""

    SM_CFG_KEY = "lastsm_and_cfg.{}"

    def __init__(self, kv) -> None:
        """Class initialization."""
        self._kv = kv

    async def run(self, rsu_id: str, cfg_info: bytes) -> None:
        """External call function."""
        cfg_info_dict = json.loads(cfg_info)
        yaml_info = cfg_info_dict.get("yaml_info")
        default.DEFAULT_ALGORITHM_YAML = yaml.safe_dump(
            yaml_info, sort_keys=False
        )
        modules.load_algorithm_modules(default)
        redis_info = cfg_info_dict.get("redis_info")
        sm_and_cfg = await self._kv.get(self.SM_CFG_KEY.format(rsu_id))
        last_sec_mark = sm_and_cfg["sm"] if sm_and_cfg.get("sm") else 0
        await self._kv.set(
            self.SM_CFG_KEY.format(rsu_id),
            {"sm": last_sec_mark, "cfg": redis_info},
        )
