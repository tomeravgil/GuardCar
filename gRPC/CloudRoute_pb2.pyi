from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DetectionRequest(_message.Message):
    __slots__ = ("frame", "width", "height", "frame_id")
    FRAME_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    FRAME_ID_FIELD_NUMBER: _ClassVar[int]
    frame: bytes
    width: int
    height: int
    frame_id: int
    def __init__(self, frame: _Optional[bytes] = ..., width: _Optional[int] = ..., height: _Optional[int] = ..., frame_id: _Optional[int] = ...) -> None: ...

class DetectionResult(_message.Message):
    __slots__ = ("detections", "frame_id")
    DETECTIONS_FIELD_NUMBER: _ClassVar[int]
    FRAME_ID_FIELD_NUMBER: _ClassVar[int]
    detections: _containers.RepeatedCompositeFieldContainer[Detection]
    frame_id: int
    def __init__(self, detections: _Optional[_Iterable[_Union[Detection, _Mapping]]] = ..., frame_id: _Optional[int] = ...) -> None: ...

class Detection(_message.Message):
    __slots__ = ("class_id", "class_name", "confidence", "x1", "y1", "x2", "y2")
    CLASS_ID_FIELD_NUMBER: _ClassVar[int]
    CLASS_NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    X1_FIELD_NUMBER: _ClassVar[int]
    Y1_FIELD_NUMBER: _ClassVar[int]
    X2_FIELD_NUMBER: _ClassVar[int]
    Y2_FIELD_NUMBER: _ClassVar[int]
    class_id: int
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float
    def __init__(self, class_id: _Optional[int] = ..., class_name: _Optional[str] = ..., confidence: _Optional[float] = ..., x1: _Optional[float] = ..., y1: _Optional[float] = ..., x2: _Optional[float] = ..., y2: _Optional[float] = ...) -> None: ...
