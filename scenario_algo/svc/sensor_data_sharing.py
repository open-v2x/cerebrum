"""Call the sensor data sharing algorithm function."""

import orjson as json
from post_process_algo import post_process
from scenario_algo.algo_lib import sensor_data_sharing
from scenario_algo.svc.collision_warning import CollisionWarning
from transform_driver import consts
from transform_driver import rsi_service


class SensorDataSharing:
    """Call the sensor data sharing algorithm function."""

    def __init__(self, kv, mqtt) -> None:
        """Class initialization."""
        self._kv = kv
        self._mqtt = mqtt
        self._exe = sensor_data_sharing.SensorDataSharing()

    async def run(self, params: dict, rsu_id: str, convert_info: list) -> None:
        """External call function."""
        # 获取traj
        ptc_traj = await self._kv.get(
            CollisionWarning.TRAJS_KEY.format(rsu_id)
        )
        motor_traj = ptc_traj["motors"] if "motors" in ptc_traj else {}
        vptc_traj = ptc_traj["vptc"] if "vptc" in ptc_traj else {}

        # 获取rsi
        rsi = await self._kv.get(rsi_service.RSI.RSI_KEY.format(rsu_id))

        # 获取rsu 经纬度
        sensor_pos = post_process.rsu_info[rsu_id]["pos"]
        msg_ssm, info_for_show = self._exe.run(
            motor_traj, vptc_traj, rsi, params, sensor_pos, convert_info
        )
        if info_for_show:
            for i in info_for_show["other_cars"]:
                post_process.convert_for_visual(i, rsu_id)
            post_process.convert_for_visual(info_for_show["ego_point"], rsu_id)
        self._mqtt.publish(
            consts.SDS_TOPIC.format(rsu_id),
            json.dumps(msg_ssm),
            0,
        )
        self._mqtt.publish(
            consts.SCENARIO_VISUAL_TOPIC.format(rsu_id),
            json.dumps([info_for_show]),
            0,
        )
