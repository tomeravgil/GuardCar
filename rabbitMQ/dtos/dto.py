from dataclasses import dataclass
from typing import Dict

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
    class_weights: Dict[int, float]