# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: system.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import nanopb_pb2 as nanopb__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0csystem.proto\x12\x06system\x1a\x0cnanopb.proto\"U\n\rDeviceControl\x12\x18\n\tdevice_id\x18\x01 \x01(\tB\x05\x92?\x02\x08@\x12\x15\n\x06\x61\x63tion\x18\x02 \x01(\tB\x05\x92?\x02\x08@\x12\x13\n\x0btemperature\x18\x03 \x01(\x05\"\x8e\x01\n\nDeviceInfo\x12\x18\n\tdevice_id\x18\x01 \x01(\tB\x05\x92?\x02\x08@\x12\x1a\n\x0b\x64\x65vice_type\x18\x02 \x01(\tB\x05\x92?\x02\x08@\x12\x11\n\x02ip\x18\x03 \x01(\tB\x05\x92?\x02\x08@\x12\x0c\n\x04port\x18\x04 \x01(\x05\x12\x14\n\x05state\x18\x05 \x01(\tB\x05\x92?\x02\x08\x10\x12\x13\n\x0btemperature\x18\x06 \x01(\x05\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'system_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _DEVICECONTROL.fields_by_name['device_id']._options = None
  _DEVICECONTROL.fields_by_name['device_id']._serialized_options = b'\222?\002\010@'
  _DEVICECONTROL.fields_by_name['action']._options = None
  _DEVICECONTROL.fields_by_name['action']._serialized_options = b'\222?\002\010@'
  _DEVICEINFO.fields_by_name['device_id']._options = None
  _DEVICEINFO.fields_by_name['device_id']._serialized_options = b'\222?\002\010@'
  _DEVICEINFO.fields_by_name['device_type']._options = None
  _DEVICEINFO.fields_by_name['device_type']._serialized_options = b'\222?\002\010@'
  _DEVICEINFO.fields_by_name['ip']._options = None
  _DEVICEINFO.fields_by_name['ip']._serialized_options = b'\222?\002\010@'
  _DEVICEINFO.fields_by_name['state']._options = None
  _DEVICEINFO.fields_by_name['state']._serialized_options = b'\222?\002\010\020'
  _DEVICECONTROL._serialized_start=38
  _DEVICECONTROL._serialized_end=123
  _DEVICEINFO._serialized_start=126
  _DEVICEINFO._serialized_end=268
# @@protoc_insertion_point(module_scope)
