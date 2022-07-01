"""Call the complement algorithm function."""

from pre_process_ai_algo.algo_lib import complement
from pre_process_ai_algo.pipelines import Base


class Interpolation(Base):
    """Call the interpolation complement algorithm function.

    1. Call the interpolation complement algorithm function.
    2. Accessing redis data required by the interpolation complement algorithm
       function.

    """

    HIS_INFO_KEY = "comple.interpl.his.{}"

    def __init__(self, kv):
        """Class initialization."""
        super().__init__(kv)
        self._exe = complement.Interpolation()


class LstmPredict(Base):
    """Call the lstm complement algorithm function.

    1. Call the lstm complement algorithm function.
    2. Accessing redis data required by the lstm complement algorithm function.

    """

    HIS_INFO_KEY = "comple.lstm.his.{}"

    def __init__(self, kv):
        """Class initialization."""
        super().__init__(kv)
        self._exe = complement.LstmPredict()
