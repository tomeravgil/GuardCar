from dataclasses import dataclass
from typing import List

@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float]

@dataclass
class DetectionResult:
    detections: List[Detection]