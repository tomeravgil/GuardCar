from abc import ABC, abstractmethod
from datetime import time
import random
from ultralytics import YOLO

class TrackingDetectionService(DetectionService):

    def __init__(self, model_path: str):
        self.tracker = 'bytetrack.yaml'
        super().__init__(model_path)
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

        self.track_history = defaultdict(lambda: [])
    
    def detect_and_process(self, frame):
        result = self.model.track(frame, stream=True, tracker=self.tracker)
        return self.handle_result(result)

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
    