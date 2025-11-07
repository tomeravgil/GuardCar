from abc import ABC
from typing import Optional

class DetectionService(ABC):
    def __init__(self, model_path: str):
        self.model = self.load_model(model_path)

    def load_model(self, model_path: Optional[str] = None):
        """Load a model from the specified path."""
        pass
        
    def detect(self, frame):
        """Perform object detection on an image."""
        pass
