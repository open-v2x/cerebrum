# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import slowspeed_grpc_pb2 as slowspeed__grpc__pb2


class SlowSpeedGrpcStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.slow_speed = channel.unary_unary(
            "/slowspeed_grpc.SlowSpeedGrpc/slow_speed",
            request_serializer=slowspeed__grpc__pb2.SlowSpeedRequest.SerializeToString,
            response_deserializer=slowspeed__grpc__pb2.SlowSpeedResponse.FromString,
        )


class SlowSpeedGrpcServicer(object):
    """Missing associated documentation comment in .proto file."""

    def slow_speed(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_SlowSpeedGrpcServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "slow_speed": grpc.unary_unary_rpc_method_handler(
            servicer.slow_speed,
            request_deserializer=slowspeed__grpc__pb2.SlowSpeedRequest.FromString,
            response_serializer=slowspeed__grpc__pb2.SlowSpeedResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "slowspeed_grpc.SlowSpeedGrpc", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class SlowSpeedGrpc(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def slow_speed(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/slowspeed_grpc.SlowSpeedGrpc/slow_speed",
            slowspeed__grpc__pb2.SlowSpeedRequest.SerializeToString,
            slowspeed__grpc__pb2.SlowSpeedResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
