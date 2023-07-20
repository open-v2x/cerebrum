"""Constants."""
import os

GRPC_PORT = str(os.getenv("GRPC_PORT", 28305))
HTTP_PORT = int(os.getenv("GRPC_PORT", 28304))
