from ..detection_service import DetectionService
from inference.models.utils import get_model
from typing import Optional

class RFDETRDetectionService(DetectionService):
    def __init__(self, model_path: str):
        self.model = self.load_model(model_path)

    def load_model(self, model_path: Optional[str] = None):
        """Load a RFDETR model from the specified path."""
        try:
            model = get_model(model_path, device="cuda")
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
        
    def detect(self, frame):
        """Perform object detection on an image."""
        return self.model.infer(frame, confidence=0.5)[0]
