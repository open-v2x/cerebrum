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

# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc  # type: ignore

from . import sensor_data_sharing_grpc_pb2 as sensor__data__sharing__grpc__pb2


class SensorDataSharingGrpcStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):  # noqa
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.sensor_data_sharing = channel.unary_unary(
            "/sensor_data_sharing_grpc.SensorDataSharingGrpc/sensor_data_sharing",  # noqa
            request_serializer=sensor__data__sharing__grpc__pb2.SensorDataSharingRequest.SerializeToString,  # noqa
            response_deserializer=sensor__data__sharing__grpc__pb2.SensorDataSharingResponse.FromString,  # noqa
        )


class SensorDataSharingGrpcServicer(object):
    """Missing associated documentation comment in .proto file."""

    def sensor_data_sharing(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_SensorDataSharingGrpcServicer_to_server(servicer, server):  # noqa
    rpc_method_handlers = {
        "sensor_data_sharing": grpc.unary_unary_rpc_method_handler(
            servicer.sensor_data_sharing,
            request_deserializer=sensor__data__sharing__grpc__pb2.SensorDataSharingRequest.FromString,  # noqa
            response_serializer=sensor__data__sharing__grpc__pb2.SensorDataSharingResponse.SerializeToString,  # noqa
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "sensor_data_sharing_grpc.SensorDataSharingGrpc", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class SensorDataSharingGrpc(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def sensor_data_sharing(
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
    ):  # noqa
        return grpc.experimental.unary_unary(
            request,
            target,
            "/sensor_data_sharing_grpc.SensorDataSharingGrpc/sensor_data_sharing",  # noqa
            sensor__data__sharing__grpc__pb2.SensorDataSharingRequest.SerializeToString,  # noqa
            sensor__data__sharing__grpc__pb2.SensorDataSharingResponse.FromString,  # noqa
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
