from ..detection_service import DetectionService
from inference.models.utils import get_model
from typing import Optional
import torch

class RFDETRDetectionService(DetectionService):
    def __init__(self, model_path: str):
        self.model = get_model(
            model_path,
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
        )

    def load_model(self, model_path: Optional[str] = None):
        """Load a RFDETR model from the specified path."""
        pass
        
    def detect(self, frame):
        """Perform object detection on an image."""
        return self.model.infer(frame, confidence=0.5)[0]
