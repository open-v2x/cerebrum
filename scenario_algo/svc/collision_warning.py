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

"""Call the collision algorithm function."""

import orjson as json
from post_process_algo import post_process
from pre_process_ai_algo.pipelines import Base
from scenario_algo.algo_lib import collision_warning
from transform_driver import consts


class CollisionWarning(Base):
    """Call the collision algorithm function.

    1. Call the collision algorithm function.
    2. Accessing redis data required by the collision algorithm function.

    """

    HIS_INFO_KEY = "collision.v2v.his.{}"
    EVENT_PAIR_KEY = "collision.event.pair.{}"
    TRAJS_KEY = "collision.trajs.{}"
    AlarmThreshold = 5  # 次数 同一对车至少发现多少次碰撞才预警
    DeleteThreshold = 10

    def __init__(self, kv, mqtt, mqtt_conn=None, node_id=None):
        """Class initialization."""
        super().__init__(kv)
        self._exe = collision_warning.CollisionWarning()
        self._mqtt = mqtt
        self._mqtt_conn = mqtt_conn
        self.node_id = node_id

    async def _filter_event(self, rsu, events: list, cwm: list) -> tuple:
        # 过滤碰撞事件
        events_count = await self._kv.get(self.EVENT_PAIR_KEY.format(rsu))
        events_count = events_count if events_count else {}
        event_list = list(events_count.keys())
        for i in event_list:
            events_count[i]["disappear_times"] += 1
        alarms = []
        filtered_cwm = []
        for index, event in enumerate(events):
            pair_key = ".".join(sorted([event["ego"], event["other"]]))
            if events_count.get(pair_key):
                events_count[pair_key]["happen_times"] += 1
                events_count[pair_key]["disappear_times"] = 0
                if (
                    events_count[pair_key]["happen_times"]
                    >= self.AlarmThreshold
                ):
                    alarms.append(event)
                    filtered_cwm.append(cwm[index])
            else:
                events_count[pair_key] = {
                    "happen_times": 1,
                    "disappear_times": 0,
                }
        for i in event_list:
            if events_count[i]["disappear_times"] >= self.DeleteThreshold:
                del events_count[i]
        await self._kv.set(self.EVENT_PAIR_KEY.format(rsu), events_count)
        return alarms, filtered_cwm

    async def run(self, rsu: str, latest_frame: dict, _: dict = {}) -> dict:
        """External call function."""
        his_info = await self._kv.get(self.HIS_INFO_KEY.format(rsu))
        context_frames = (
            his_info["context_frames"]
            if his_info.get("context_frames")
            else {}
        )
        last_ts = his_info["last_ts"] if his_info.get("last_ts") else 0
        cwm, events, last_ts, motors_trajs, vptc_trajs = self._exe.run(
            context_frames, latest_frame, last_ts
        )
        await self._kv.set(
            self.HIS_INFO_KEY.format(rsu),
            {
                "context_frames": context_frames,
                "last_ts": last_ts,
                "latest_frame": latest_frame,
            },
        )
        await self._kv.set(
            self.TRAJS_KEY.format(rsu),
            {"motors": motors_trajs, "vptc": vptc_trajs},
        )
        if events:
            alarms, filtered_cwm = await self._filter_event(rsu, events, cwm)
            post_process.convert_for_collision_visual(alarms, rsu)
            collision_warning_message = post_process.generate_cwm(
                filtered_cwm, rsu
            )
            if alarms:
                if self._mqtt_conn:
                    self._mqtt_conn.publish(
                        consts.CW_VISUAL_TOPIC.format(rsu, self.node_id),
                        json.dumps(alarms),
                        0,
                    )
                self._mqtt.publish(
                    consts.CW_TOPIC.format(rsu),
                    json.dumps(collision_warning_message),
                    0,
                )
        return latest_frame
