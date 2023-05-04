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
"""svc."""
from overspeed_warning_service.algo import (  # type: ignore
    OverSpeedWarning as OverSpeedWarningAlgoLib,
)  # noqa


class OverSpeedWarning:
    """Call the overspeed warning algorithm function."""

    def __init__(self):
        """Class initialization."""
        self._exe = OverSpeedWarningAlgoLib()

    async def run(
        self,
        latest_frame: dict,
        context_frames: dict,
        last_ts: int,
        speed_limits: dict,
    ):
        """External call function."""
        osw, show_info = self._exe.run(
            context_frames, latest_frame, last_ts, speed_limits
        )
        return osw, show_info
