"""Send processed data to RSU and central platform."""

from config import devel as cfg
import orjson as json
from post_process_algo import post_process
from pre_process_ai_algo.pipelines import Base
from transform_driver import consts
from transform_driver import rsi_service
from typing import Any
from typing import Dict


class Visualize(Base):
    """Send processed data to rsu and central platform."""

    def __init__(self, kv, mqtt):
        """Class initialization."""
        super().__init__(kv)
        self._mqtt = mqtt

    async def run(self, rsu: str, latest_frame: dict, _: dict = {}) -> dict:
        """External call function."""
        # 可视化，修改 x，y 后，返回给 mqtt
        vis = []
        info_dict: Dict[str, Any] = {
            "motor": 0,
            "non-motor": 0,
            "pedestrian": 0,
            "motor_speed": 0,
        }
        for fr in latest_frame.values():
            frame = fr.copy()
            post_process.convert_for_visual(frame, rsu)
            info_dict[frame["ptcType"]] += 1
            if frame["ptcType"] == "motor":
                info_dict["motor_speed"] += frame["speed"] * 0.02 * 3.6
            vis.append(frame)
        info_dict["motor_speed"] = (
            info_dict["motor_speed"] / info_dict["motor"]
            if info_dict["motor"]
            else 0
        )
        # 获取rsi
        congestion = await self._kv.get(
            rsi_service.RSI.CONGESTION_KEY.format(rsu)
        )
        if congestion:
            congestion_info = "congestion"
        else:
            congestion_info = "free flow"
        final_info = {
            "rsuEsn": rsu,
            "vehicleTotal": info_dict["motor"],
            "averageSpeed": info_dict["motor_speed"],
            "pedestrianTotal": info_dict["pedestrian"],
            "congestion": congestion_info,
        }
        url = cfg.cloud_server + "/homes/route_info_push"
        await post_process.http_post(url, final_info)
        self._mqtt.publish(
            consts.RSM_VISUAL_TOPIC.format(rsu), json.dumps(vis), 0
        )
        return latest_frame
