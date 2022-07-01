"""Algorithm pipeline processing flow."""

import orjson as json
from post_process_algo import post_process
from pre_process_ai_algo.pipelines.complement import Interpolation
from pre_process_ai_algo.pipelines.complement import LstmPredict
from pre_process_ai_algo.pipelines.fusion import Fusion
from pre_process_ai_algo.pipelines.smooth import ExponentialSmooth
from pre_process_ai_algo.pipelines.smooth import PolynomialSmooth
from pre_process_ai_algo.pipelines.visualization import Visualize
from scenario_algo.svc.collision_warning import CollisionWarning
from transform_driver import consts


class DataProcessing:
    """Convert rsm data format to algorithm format data."""

    LOCK_KEY = "v2x.process.lock.{}"
    SM_CFG_KEY = "lastsm_and_cfg.{}"

    def __init__(self, mqtt, kv) -> None:
        """Class initialization."""
        self._interpolation = Interpolation(kv)
        self._fusion = Fusion(kv)
        self._exponential_smooth = ExponentialSmooth(kv)
        self._lstm_predict = LstmPredict(kv)
        self._polynomial_smooth = PolynomialSmooth(kv)
        self._collision_warning = CollisionWarning(kv, mqtt)
        self._visual = Visualize(kv, mqtt)
        self._kv = kv
        self._mqtt = mqtt
        self._pipelines = [
            "fusion",
            "complement",
            "smooth",
            "visual",
            "collision",
        ]
        self._fusion_dispatch = {
            0: False,
            1: self._fusion,
        }
        self._smooth_dispatch = {
            0: False,
            1: self._exponential_smooth,
            2: self._polynomial_smooth,
        }
        self._complement_dispatch = {
            0: False,
            1: self._interpolation,
            2: self._lstm_predict,
        }
        self._visual_dispatch = {
            0: False,
            1: self._visual,
        }
        self._collision_dispatch = {
            0: False,
            1: self._collision_warning,
        }

    async def run(
        self, rsu_id: str, raw_rsm: dict, miss_flag: str, miss_info: str
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
                sm_and_cfg["cfg"]
                if sm_and_cfg.get("cfg")
                else {
                    "fusion": 0,
                    "complement": 1,
                    "smooth": 1,
                    "collision": 1,
                    "visual": 1,
                }
            )
            if (
                current_sec_mark <= last_sec_mark
                and last_sec_mark - current_sec_mark < 50000
            ):
                return None
            await self._kv.set(
                self.SM_CFG_KEY.format(rsu_id),
                {"sm": current_sec_mark, "cfg": pipe_cfg},
            )
            pipelines = [
                getattr(self, "_{}_dispatch".format(p))[pipe_cfg[p]]
                for p in self._pipelines
            ]
            for p in pipelines:
                if p:
                    latest = await p.run(rsu_id, latest)
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
        cfg_info = json.loads(cfg_info)
        sm_and_cfg = await self._kv.get(self.SM_CFG_KEY.format(rsu_id))
        last_sec_mark = sm_and_cfg["sm"] if sm_and_cfg.get("sm") else 0
        await self._kv.set(
            self.SM_CFG_KEY.format(rsu_id),
            {"sm": last_sec_mark, "cfg": cfg_info},
        )
