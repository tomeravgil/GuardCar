from abc import ABC, abstractmethod
from typing import Optional

from detection.dto.detection_types import DetectionResult

class DetectionService(ABC):
    def __init__(self, model_path: str):
        self.model = self.load_model(model_path)

    @abstractmethod
    def load_model(self, model_path: Optional[str] = None):
        """Load a model from the specified path."""
        pass
        
    @abstractmethod
    def detect(self, frame) -> DetectionResult:
        """Perform object detection on an image."""
        pass

    @abstractmethod
    def get_classes(self):
        """Get the classes name to id"""
        pass