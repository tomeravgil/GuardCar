from abc import ABC, abstractmethod
from datetime import time
import random
from ultralytics import YOLO

class DetectionService(ABC):
    def __init__(self, model_path: str):
        self.model = self.load_model(model_path)

    def load_model(self, model_path: str):
        """Load a YOLO model from the specified path."""
        try:
            model = YOLO(model_path)
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
        
    def detect_and_process(self):
        """Perform object detection on an image and display the results."""
        pass

    @abstractmethod
    def handle_result(self, result):
        """Abstract method to handle each detection result."""
        pass
