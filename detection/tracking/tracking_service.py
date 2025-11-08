import time
import numpy as np
from collections import defaultdict

from supervision.tracker.byte_tracker.core import ByteTrack
from supervision.detection.core import Detections


class TrackingDetectionService:
    def __init__(self):
        self.tracker = ByteTrack()
        self.first_seen = defaultdict(lambda: time.time())

        self.class_to_score = {
            0: 0.05,
            1: 0.01,
            2: 0.04,
            3: 0.02,
            5: 0.04,
            7: 0.04
        }

    def process_detections(self, detections, frame_shape):
        if not detections:
            return 0.0, Detections.empty()

        H, W = frame_shape

        # Convert raw dets → supervision.Detections
        xyxy = np.array([d["bbox"] for d in detections], dtype=float)
        confidence = np.array([d["conf"] for d in detections], dtype=float)
        class_id = np.array([d["cls_id"] for d in detections], dtype=int)

        det = Detections(
            xyxy=xyxy,
            confidence=confidence,
            class_id=class_id
        )

        tracked = self.tracker.update_with_detections(det)

        # If no objects tracked → no score
        if len(tracked) == 0:
            return 0.0, tracked

        scores = []
        for i in range(len(tracked)):
            x1, y1, x2, y2 = tracked.xyxy[i]
            cls_id = int(tracked.class_id[i])
            conf = float(tracked.confidence[i])
            track_id = int(tracked.tracker_id[i])

            area_ratio = (x2 - x1) * (y2 - y1) / (W * H)

            # ✅ Only initialize first_seen once per track_id
            if track_id not in self.first_seen:
                self.first_seen[track_id] = time.time()
            duration = time.time() - self.first_seen[track_id]

            class_bonus = self.class_to_score.get(cls_id, 0.0) * conf

            scores.append((area_ratio, duration, class_bonus))

        return self._score(scores), tracked


    def _score(self, scores):
        areas, times, classes = zip(*scores)
        def norm(values):
            mn, mx = min(values), max(values)
            return [(v - mn) / (mx - mn + 1e-9) for v in values]
        A, T, C = norm(areas), norm(times), norm(classes)
        return sum((1/6*a + 0.5*t + 1/3*c) for a, t, c in zip(A, T, C)) / len(A)
