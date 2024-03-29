# -*- coding: utf-8 -*-
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

# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: collision_grpc.proto
"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf.internal import builder as _builder
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x14\x63ollision_grpc.proto\x12\x0e\x63ollision_grpc" \n\x10\x43ollisionRequest\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t"!\n\x11\x43ollisionResponse\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\t2c\n\rCollisionGrpc\x12R\n\tcollision\x12 .collision_grpc.CollisionRequest\x1a!.collision_grpc.CollisionResponse"\x00\x62\x06proto3'  # noqa
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, "collision_grpc_pb2", globals()
)
if _descriptor._USE_C_DESCRIPTORS == False:  # noqa
    DESCRIPTOR._options = None
    _COLLISIONREQUEST._serialized_start = 40  # noqa
    _COLLISIONREQUEST._serialized_end = 72  # noqa
    _COLLISIONRESPONSE._serialized_start = 74  # noqa
    _COLLISIONRESPONSE._serialized_end = 107  # noqa
    _COLLISIONGRPC._serialized_start = 109  # noqa
    _COLLISIONGRPC._serialized_end = 208  # noqa
# @@protoc_insertion_point(module_scope)
