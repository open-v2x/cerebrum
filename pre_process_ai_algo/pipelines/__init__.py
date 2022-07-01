"""Call algorithm function."""


class Base:
    """Call algorithm function and call redis to access data."""

    HIS_INFO_KEY = ""

    def __init__(self, kv):
        """Class initialization."""
        self._kv = kv

    async def run(self, rsu: str, latest_frame: dict, _: dict = {}) -> dict:
        """External call function."""
        his_info = await self._kv.get(self.HIS_INFO_KEY.format(rsu))
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
            self.HIS_INFO_KEY.format(rsu),
            {"context_frames": context_frames, "last_ts": last_ts},
        )
        return ret
