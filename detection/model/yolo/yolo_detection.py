from ultralytics import YOLO
from typing import Optional
from detection.model.detection_service import DetectionService

class YOLODetectionService(DetectionService):
    def __init__(self, model_path: str):
        self.model = self.load_model(model_path)

    def load_model(self, model_path: Optional[str] = None):
        """Load a YOLO model from the specified path."""
        try:
            model = YOLO(model_path)
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
        
    def detect(self, frame):
        """Perform object detection on an image."""
        return self.model.predict(frame)