# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: slowspeed_grpc.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x14slowspeed_grpc.proto\x12\x0eslowspeed_grpc" \n\x10SlowSpeedRequest\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t"!\n\x11SlowSpeedResponse\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t2d\n\rSlowSpeedGrpc\x12S\n\nslow_speed\x12 .slowspeed_grpc.SlowSpeedRequest\x1a!.slowspeed_grpc.SlowSpeedResponse"\x00\x62\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "slowspeed_grpc_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _SLOWSPEEDREQUEST._serialized_start = 40
    _SLOWSPEEDREQUEST._serialized_end = 72
    _SLOWSPEEDRESPONSE._serialized_start = 74
    _SLOWSPEEDRESPONSE._serialized_end = 107
    _SLOWSPEEDGRPC._serialized_start = 109
    _SLOWSPEEDGRPC._serialized_end = 209
# @@protoc_insertion_point(module_scope)