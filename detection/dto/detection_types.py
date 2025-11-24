from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Detection:
    class_id: Optional[int]
    class_name: str
    confidence: float
    bbox: List[float]

@dataclass
class DetectionResult:
    detections: List[Detection]