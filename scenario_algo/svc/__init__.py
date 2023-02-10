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

"""Call algorithm function."""


class Base:
    """Call algorithm function and call redis to access data."""

    HIS_INFO_KEY = ""

    def __init__(self, kv):
        """Class initialization."""
        self._kv = kv

    async def run(
        self,
        rsu: str,
        intersection_id: str,
        latest_frame: dict,
        node_id: int,
        _: dict = {},
    ) -> dict:
        """External call function."""
        his_info = await self._kv.get(
            self.HIS_INFO_KEY.format(intersection_id)
        )
        context_frames = (
            his_info["context_frames"]
            if his_info.get("context_frames")
            else {}
        )
        last_ts = his_info["last_ts"] if his_info.get("last_ts") else 0
        ret, last_ts = self._exe.run(  # type: ignore
            context_frames, latest_frame, last_ts
        )
        await self._kv.set(
            self.HIS_INFO_KEY.format(intersection_id),
            {"context_frames": context_frames, "last_ts": last_ts},
        )
        return ret
