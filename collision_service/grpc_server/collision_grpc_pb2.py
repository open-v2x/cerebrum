# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: collision_grpc.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x14\x63ollision_grpc.proto\x12\x0e\x63ollision_grpc" \n\x10\x43ollisionRequest\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t"!\n\x11\x43ollisionResponse\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t2c\n\rCollisionGrpc\x12R\n\tcollision\x12 .collision_grpc.CollisionRequest\x1a!.collision_grpc.CollisionResponse"\x00\x62\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "collision_grpc_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _COLLISIONREQUEST._serialized_start = 40
    _COLLISIONREQUEST._serialized_end = 72
    _COLLISIONRESPONSE._serialized_start = 74
    _COLLISIONRESPONSE._serialized_end = 107
    _COLLISIONGRPC._serialized_start = 109
    _COLLISIONGRPC._serialized_end = 208
# @@protoc_insertion_point(module_scope)
