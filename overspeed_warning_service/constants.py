"""Constants."""
import os

COORDINATE_UNIT: int = 10**7  # 新四跨协议规定的经纬度单位转换unit
MAX_SEC_MARK: int = 60000  # 新四跨中对secMark的规定中的最大值
HISTORICAL_INTERVAL: int = 1600  # 同一id容纳的历史数据时间范围
UPDATE_INTERVAL: int = 1600  # 某一id可容忍的不更新数据的时间范围

GRPC_PORT = str(os.getenv("GRPC_PORT", 28303))
HTTP_PORT = int(os.getenv("GRPC_PORT", 28302))
