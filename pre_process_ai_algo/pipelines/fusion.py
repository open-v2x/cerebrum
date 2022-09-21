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

"""Call the fusion algorithm function."""

from common import modules
from pre_process_ai_algo.pipelines import Base

fusion = modules.algorithms.pre_process_fusion


class Fusion(Base):
    """Call the fusion algorithm function.

    1. Call the fusion algorithm function.
    2. Accessing redis data required by the fusion algorithm function.

    """

    HIS_INFO_KEY = "fusion.f.his.{}"

    def __init__(self, kv):
        """Class initialization."""
        super().__init__(kv)
        self._exe = fusion.Fusion()

    async def run(self, rsu: str, latest_frame: dict, _: dict = {}) -> dict:
        """External call function."""
        his_info = await self._kv.get(self.HIS_INFO_KEY.format(rsu))
        context_frames = (
            his_info["context_frames"]
            if his_info.get("context_frames")
            else {}
        )
        last_ts = his_info["last_ts"] if his_info.get("last_ts") else 0
        match = his_info["match"] if his_info.get("match") else {}
        ret, last_ts, match = self._exe.run(
            context_frames, latest_frame, last_ts, match
        )
        await self._kv.set(
            self.HIS_INFO_KEY.format(rsu),
            {
                "context_frames": context_frames,
                "last_ts": last_ts,
                "match": match,
            },
        )
        return ret
