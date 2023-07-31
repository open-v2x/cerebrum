"""Constants."""
import os

COORDINATE_UNIT: int = 10**7  # 新四跨协议规定的经纬度单位转换unit
GRPC_PORT = str(os.getenv("GRPC_PORT", 28305))
HTTP_PORT = int(os.getenv("GRPC_PORT", 28304))
