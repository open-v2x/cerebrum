# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: congestion_grpc.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x15\x63ongestion_grpc.proto\x12\x0f\x63ongestion_grpc"!\n\x11\x43ongestionRequest\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t""\n\x12\x43ongestionResponse\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t2i\n\x0e\x43ongestionGrpc\x12W\n\ncongestion\x12".congestion_grpc.CongestionRequest\x1a#.congestion_grpc.CongestionResponse"\x00\x62\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "congestion_grpc_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _CONGESTIONREQUEST._serialized_start = 42
    _CONGESTIONREQUEST._serialized_end = 75
    _CONGESTIONRESPONSE._serialized_start = 77
    _CONGESTIONRESPONSE._serialized_end = 111
    _CONGESTIONGRPC._serialized_start = 113
    _CONGESTIONGRPC._serialized_end = 218
# @@protoc_insertion_point(module_scope)
