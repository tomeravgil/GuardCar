from dataclasses import dataclass
from typing import Dict,Literal


@dataclass
class SuspicionFrameMessage:
    suspicion_score: float

@dataclass
class RecordingStatusMessage:
    recording: bool

@dataclass
class CloudProviderConfigMessage:
    provider_name: str
    connection_ip: str
    server_certification: str
    delete: bool

@dataclass
class SuspicionConfigMessage:
    threshold: int
    class_weights: Dict[str, float]

@dataclass
class ResponseMessage:
    success: bool
    message: str
    related_to: Literal["cloud", "suspicion", "general"]

@dataclass
class VideoFrameMessage:
    jpeg_bytes: str
