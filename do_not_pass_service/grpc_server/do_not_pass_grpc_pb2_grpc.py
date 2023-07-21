# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import do_not_pass_grpc_pb2 as do__not__pass__grpc__pb2


class DoNotPassGrpcStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.do_not_pass = channel.unary_unary(
            "/do_not_pass_grpc.DoNotPassGrpc/do_not_pass",
            request_serializer=do__not__pass__grpc__pb2.DoNotPassRequest.SerializeToString,
            response_deserializer=do__not__pass__grpc__pb2.DoNotPassResponse.FromString,
        )


class DoNotPassGrpcServicer(object):
    """Missing associated documentation comment in .proto file."""

    def do_not_pass(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_DoNotPassGrpcServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "do_not_pass": grpc.unary_unary_rpc_method_handler(
            servicer.do_not_pass,
            request_deserializer=do__not__pass__grpc__pb2.DoNotPassRequest.FromString,
            response_serializer=do__not__pass__grpc__pb2.DoNotPassResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "do_not_pass_grpc.DoNotPassGrpc", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class DoNotPassGrpc(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def do_not_pass(
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
            "/do_not_pass_grpc.DoNotPassGrpc/do_not_pass",
            do__not__pass__grpc__pb2.DoNotPassRequest.SerializeToString,
            do__not__pass__grpc__pb2.DoNotPassResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
