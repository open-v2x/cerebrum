"""Call the smooth algorithm function."""

from pre_process_ai_algo.algo_lib import smooth
from pre_process_ai_algo.pipelines import Base


class PolynomialSmooth(Base):
    """Call the polynomial smooth algorithm function.

    1. Call the polynomial smooth algorithm function.
    2. Accessing redis data required by the polynomial smooth algorithm
       function.

    """

    HIS_INFO_KEY = "smooth.polyn.his.{}"

    def __init__(self, kv):
        """Class initialization."""
        super().__init__(kv)
        self._exe = smooth.Polynomial()


class ExponentialSmooth(Base):
    """Call the exponential smooth algorithm function.

    1. Call the exponential smooth algorithm function.
    2. Accessing redis data required by the exponential smooth algorithm
       function.

    """

    HIS_INFO_KEY = "smooth.exp.his.{}"

    def __init__(self, kv):
        """Class initialization."""
        super().__init__(kv)
        self._exe = smooth.Exponential()
