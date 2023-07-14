from google.protobuf import descriptor as _descriptor  # type: ignore
from google.protobuf import message as _message  # type: ignore
from typing import ClassVar as _ClassVar, Optional as _Optional  # type: ignore

DESCRIPTOR: _descriptor.FileDescriptor

class DoNotPassRequest(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: str

    def __init__(self, data: _Optional[str] = ...) -> None: ...

class DoNotPassResponse(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: str

    def __init__(self, data: _Optional[str] = ...) -> None: ...
