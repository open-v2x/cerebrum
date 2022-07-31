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

"""Algorithm service consts and mqtt topic config."""

from config import devel as cfg
from transform_driver import db

MaxSecMark = 60000  # 新四跨中对secMark的规定中的最大值
CoordinateUnit = 10**7  # 新四跨协议规定的经纬度单位转换unit


def topic_replace(topic: str, delimiter: str) -> str:
    """Topic delimiter conversion for mqtt."""
    return topic.replace("/", delimiter)


# RSM
RSM_DOWN_TOPIC = topic_replace("V2X/RSU/{}/RSM/DOWN", cfg.DELIMITER)
RSM_STD_ACK_TOPIC = topic_replace("V2X/RSU/{}/RSM/ACK", cfg.DELIMITER)
RSM_DAWNLINE_ACK_TOPIC = topic_replace(
    "V2X/RSU/{}/RSM/DAWNLINE/ACK", cfg.DELIMITER
)

# RSI
RSI_DOWN_TOPIC = topic_replace("V2X/RSU/{}/RSI/DOWN", cfg.DELIMITER)
RSI_UP_TOPIC = topic_replace("V2X/RSU/{}/RSI/UP", cfg.DELIMITER)

# scenario
CW_TOPIC = topic_replace("V2X/RSU/{}/CWM/DOWN", cfg.DELIMITER)
SDS_TOPIC = topic_replace("V2X/RSU/{}/SDS/DOWN", cfg.DELIMITER)
CLC_TOPIC = topic_replace("V2X/RSU/{}/CLC/DOWN", cfg.DELIMITER)
DNP_TOPIC = topic_replace("V2X/RSU/{}/DNP/DOWN", cfg.DELIMITER)

if db.node_id is not None:
    # RSM visual
    RSM_VISUAL_TOPIC = topic_replace(
        "V2X/DEVICE/{}/PARTICIPANT/NODE" + str(db.node_id), cfg.DELIMITER
    )
    # scenario visual
    CW_VISUAL_TOPIC = topic_replace(
        "V2X/DEVICE/{}/APPLICATION/CW/NODE" + str(db.node_id), cfg.DELIMITER
    )
    CLC_VISUAL_TOPIC = topic_replace(
        "V2X/DEVICE/{}/APPLICATION/CLC/NODE" + str(db.node_id), cfg.DELIMITER
    )
    DNP_VISUAL_TOPIC = topic_replace(
        "V2X/DEVICE/{}/APPLICATION/DNP/NODE" + str(db.node_id), cfg.DELIMITER
    )
    SDS_VISUAL_TOPIC = topic_replace(
        "V2X/DEVICE/{}/APPLICATION/SDS/NODE" + str(db.node_id), cfg.DELIMITER
    )
