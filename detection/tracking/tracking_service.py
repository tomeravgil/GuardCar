import time
from collections import defaultdict
from ultralytics import YOLO

class TrackingDetectionService:

    def __init__(self):
        self.tracker = 'bytetrack.yaml'

        # TODO make it so the user can set these values
        self.class_to_score = {
            0: 0.05,  # person
            1: 0.01,  # bicycle
            2: 0.04,  # car
            3: 0.02,  # motorcycle
            5: 0.04,  # bus
            7: 0.04   # truck
        }

        self.first_seen = {}
        self.track_history = defaultdict(list)
    
    def process_frame(self, result):
        """Handle the detection result for an image."""
        detections = []
        for box in result.boxes:
            xyxy = box.xyxy[0].cpu().numpy()   # [x1, y1, x2, y2]
            conf = float(box.conf[0] )   # confidence

            cls = int(box.cls[0]) # class id
            track_id = int(box.id[0]) if box.id is not None else None  # tracking id
            if track_id is not None and track_id not in self.first_seen:
                self.first_seen[track_id] = time.time()

            area_score = self._calculate_area(result, xyxy)
            time_score = self._track_duration(track_id)
            class_score = self.class_to_score.get(cls, 0.0) * conf
            detections.append((area_score, time_score, class_score))

        if len(detections) == 0:
            return 0.0
        norm_scores = self._normalize_components(detections)
        return sum(norm_scores) / len(norm_scores)
            
    def _calculate_area(self, result, xyxy):
        bounding_box_area = self._get_area_of_confidence(xyxy)
        photo_area = result.orig_shape[0] * result.orig_shape[1]
        area_ratio = bounding_box_area / photo_area
        return area_ratio

    def _track_duration(self, track_id):
        if track_id not in self.first_seen:
            return 0.0
        return time.time() - self.first_seen[track_id]
    
    def _normalize_components(self, detections):
        # detections = [(area, time, class), ...]
        areas = [d[0] for d in detections]
        times = [d[1] for d in detections]
        classes = [d[2] for d in detections]

        n_area = self._norm(areas)
        n_time = self._norm(times)
        n_class = self._norm(classes)

        # Weighted sum
        weights = (1/6, 0.5, 1/3)
        scores = [
            weights[0] * a + weights[1] * t + weights[2] * c
            for a, t, c in zip(n_area, n_time, n_class)
        ]
        return scores

    def _norm(self, values):
        mn, mx = min(values), max(values)
        return [(v - mn) / (mx - mn + 1e-9) for v in values]
    
    def _get_area_of_confidence(self, xyxy):
        """Calculate the area of the bounding box."""
        x1, y1, x2, y2 = map(int, xyxy)
        return (x2 - x1) * (y2 - y1)
    