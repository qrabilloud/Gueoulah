# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: showtime.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'showtime.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import super_pb2 as super__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0eshowtime.proto\x1a\x0bsuper.proto\"\'\n\x08Schedule\x12\x1b\n\x08schedule\x18\x01 \x03(\x0b\x32\t.TimeShow\"\x19\n\tMovieDate\x12\x0c\n\x04\x64\x61te\x18\x01 \x01(\t\"\x19\n\x07MovieID\x12\x0e\n\x06movies\x18\x01 \x03(\t2X\n\x08ShowTime\x12(\n\x0eGetMovieByDate\x12\n.MovieDate\x1a\x08.MovieID\"\x00\x12\"\n\x0bGetSchedule\x12\x06.Empty\x1a\t.Schedule\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'showtime_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_SCHEDULE']._serialized_start=31
  _globals['_SCHEDULE']._serialized_end=70
  _globals['_MOVIEDATE']._serialized_start=72
  _globals['_MOVIEDATE']._serialized_end=97
  _globals['_MOVIEID']._serialized_start=99
  _globals['_MOVIEID']._serialized_end=124
  _globals['_SHOWTIME']._serialized_start=126
  _globals['_SHOWTIME']._serialized_end=214
# @@protoc_insertion_point(module_scope)
