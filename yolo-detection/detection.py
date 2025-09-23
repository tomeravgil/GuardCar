import cv2
import random
from ultralytics import YOLO
from google.colab.patches import cv2_imshow

def getColours(cls_num):
    """Generate unique colors for each class ID"""
    random.seed(cls_num)
    return tuple(random.randint(0, 255) for _ in range(3))


class DetectionService:
    def __init__(self, model_path: str, streaming_file_path: str = None):
        self.model = self.load_model(model_path)
        self.streaming_urls = []
        self.id_tracker = []
        if streaming_file_path:
            self.load_streaming_urls(streaming_file_path)

    def load_model(self, model_path: str) -> YOLO:
        """Load a YOLO model from the specified path."""
        try:
            model = YOLO(model_path)
            return model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
        
    def load_streaming_urls(self, streaming_file_path: str):
        """Load streaming URLs from a text file."""
        try:
            with open(streaming_file_path, 'r') as file:
                self.streaming_urls = [line.strip() for line in file if line.strip()]
        except Exception as e:
            print(f"Error loading streaming URLs: {e}")
        
    def detect_and_display(self):
        """Perform object detection on an image and display the results."""
        
        for source_file in self.streaming_urls:
            for result in self.model(source_file, stream=True):
                pass
