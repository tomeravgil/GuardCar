import time
import numpy as np
from collections import defaultdict
import math
from supervision.tracker.byte_tracker.core import ByteTrack
from supervision.detection.core import Detections



class TrackingDetectionService:
    def __init__(self):
        # ByteTrack tuned for webcam tracking stability
        self.tracker = ByteTrack(
            lost_track_buffer=30,
            frame_rate=30,
            minimum_consecutive_frames=15,
        )

        # Store the timestamp when each track_id first appeared
        self.first_seen = {}
        self.last_seen = {}

        # Class weighting bonus
        self.class_to_score = {
            0: 0.12,  # person: biggest threat
            1: 0.01,  # bicycle: basically irrelevant
            2: 0.04,  # car
            3: 0.04,  # motorcycle
            5: 0.06,  # bus
            7: 0.06   # truck
        }


        # Max score scaling target
        self.max_score = 100.0


    def process_detections(self, detections, frame_shape):
        if not detections:
            self._cleanup_lost_tracks()
            return 0.0, Detections.empty()

        H, W = frame_shape

        xyxy = np.array([d["bbox"] for d in detections], dtype=float)
        conf = np.array([d["conf"] for d in detections], dtype=float)
        cls = np.array([d["cls_id"] for d in detections], dtype=int)

        det = Detections(xyxy=xyxy, confidence=conf, class_id=cls)
        tracked = self.tracker.update_with_detections(det)

        # No tracks
        if len(tracked) == 0:
            self._cleanup_lost_tracks()
            return 0.0, tracked

        scores = []
        base_class_scores = []
        now = time.time()

        for i in range(len(tracked)):
            x1, y1, x2, y2 = tracked.xyxy[i]
            cls_id = int(tracked.class_id[i])
            conf = float(tracked.confidence[i])
            track_id = int(tracked.tracker_id[i])

            area_ratio = (((x2 - x1) * (y2 - y1)) / (W * H))*100

            # Initialize timestamp if new track
            if track_id not in self.first_seen:
                self.first_seen[track_id] = now
            self.last_seen[track_id] = now

            duration = now - self.first_seen[track_id]

            # A) Baseline score (smooth growth)
            baseline = (
                self.sigmoid(area_ratio, 50) +
                self.sigmoid(duration, 30)
            )
            base_class_scores.append(self.class_to_score.get(cls_id, 0.0) * conf)
            scores.append(baseline)

        self._cleanup_lost_tracks()
        class_influence = np.mean(base_class_scores) * 50
        final_score = min(np.mean(scores) + class_influence, self.max_score)
        return final_score, tracked


    def _cleanup_lost_tracks(self):
        now = time.time()
        remove_ids = [tid for tid, last in self.last_seen.items() if now - last > 1.0]
        for tid in remove_ids:
            self.first_seen.pop(tid, None)
            self.last_seen.pop(tid, None)

    def sigmoid(self, x, scale, max=0):
        scaled_coefficient = (.2*scale)/scale
        return scale / (1+math.exp(-(x-(max/2))*scaled_coefficient))