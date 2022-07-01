"""Call the fusion algorithm function."""

from pre_process_ai_algo.algo_lib import fusion
from pre_process_ai_algo.pipelines import Base


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
