from abc import ABC, abstractmethod
from datetime import time
import random
from ultralytics import YOLO

def getColours(cls_num):
    """Generate unique colors for each class ID"""
    random.seed(cls_num)
    return tuple(random.randint(0, 255) for _ in range(3))


class DetectionService(ABC):
    def __init__(self, model_path: str, streaming_file_path: str = None):
        self.model = self.load_model(model_path)
        self.streaming_urls = []
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
        
    def detect_and_process(self):
        """Perform object detection on an image and display the results."""

        for source_file in self.streaming_urls:
            for result in self.model.track(source_file, stream=True, tracker=self.tracker):
                self.handle_result(result)


    @abstractmethod
    def handle_result(self, result):
        """Abstract method to handle each detection result."""
        pass

class TrackingDetectionService(DetectionService):

    def __init__(self, model_path: str, streaming_file_path: str = None):
        self.tracker = 'bytetrack.yaml'
        super().__init__(model_path, streaming_file_path)
        self.ids = {}

        # TODO make it so the user can set these values
        self.class_to_score = {
            0: 0.05,  # person
            1: 0.01,  # bicycle
            2: 0.04,  # car
            3: 0.02,  # motorcycle
            5: 0.04,  # bus
            7: 0.04   # truck
        }

    def handle_result(self, result):
        """Handle the detection result for an image."""

        boxes = result.boxes  
        normalization_scores = []
        for box in boxes:
            xyxy = box.xyxy[0].cpu().numpy()   # [x1, y1, x2, y2]
            conf = box.conf[0].cpu().item()    # confidence

            cls  = int(box.cls[0].cpu().item()) # class id
            id   = int(box.id[0].cpu().item())  # tracking id
            if id not in self.ids:
                self.ids[id] = time.time()

            box_score = self._calculate_area(result, xyxy) * (1/6)
            time_score = time.time() - self.ids[id] * .5
            class_score = 1e-10 # to avoid multiplication by zero
            if cls in self.class_to_score:

                # multiply by confidence to give more weight to high confidence detections
                class_score = (self.class_to_score[cls]*conf) * (1/3)

            normalization_score = self._calculate_normalization_score(box_score, time_score, class_score)
            normalization_scores.append((normalization_score, id, cls, conf, xyxy))

        average_score = sum(normalization_scores) / len(normalization_scores)
        return average_score if normalization_scores else 0.0
            

    def _calculate_area(self, result, xyxy):
        bounding_box_area = self._get_area_of_confidence(xyxy)
        photo_area = result.orig_shape[0] * result.orig_shape[1]
        area_ratio = bounding_box_area / photo_area
        return area_ratio
    
    def _calculate_normalization_score(self, box_score, time_score, class_score):
        total_score = 0
        scores = [box_score, time_score, class_score]
        weights = [(1/6), .5, (1/3)]
        for i in range(len(scores)):
            x_norm = (score[i] - min(scores[i])) / (max(scores[i]) - min(scores[i]) + 1e-10)
            total_score += x_norm * weights[i]
        return total_score

    def _get_area_of_confidence(self, xyxy):
        """Calculate the area of the bounding box."""
        x1, y1, x2, y2 = map(int, xyxy)
        return (x2 - x1) * (y2 - y1)
    