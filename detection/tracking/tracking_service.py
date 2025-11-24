import time
import numpy as np
from collections import defaultdict
import math
from supervision.tracker.byte_tracker.core import ByteTrack
from supervision.detection.core import Detections

class TrackingDetectionService:
    def __init__(self):
        # ByteTrack tuned for tracking stability
        self.tracker = ByteTrack(
            lost_track_buffer=30,
            frame_rate=30,
            minimum_consecutive_frames=15,
        )

        # Store the timestamp when each track_id first appeared
        self.first_seen = {}
        self.last_seen = {}

        # Class weighting bonus
        self.class_k = {
            0: 1.6,   # person → rises much faster
            1: 0.6,   # bicycle → slow rise
            2: 1.0,   # car → normal
            3: 1.0,   # motorcycle
            5: 1.4,   # bus → bigger = more contextual threat
            7: 1.4,   # truck
        }
        # Max score scaling target
        self.max_score = 100.0

    def process_detections(self, detections, frame_shape):
        if not detections:
            self._cleanup_lost_tracks()
            return 0.0, Detections.empty()

        H, W = frame_shape

        xyxy = np.array([d.bbox for d in detections], dtype=float)
        conf = np.array([d.confidence for d in detections], dtype=float)
        cls  = np.array([d.class_id for d in detections], dtype=int)

        det = Detections(xyxy=xyxy, confidence=conf, class_id=cls)
        tracked = self.tracker.update_with_detections(det)

        # No tracks
        if len(tracked) == 0:
            self._cleanup_lost_tracks()
            return 0.0, tracked

        scores = []
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
            k_factor = self.class_k.get(cls_id, 1.0)

            area_score = self.sigmoid(area_ratio, midpoint=25, k=0.12 * k_factor, max_value=60)
            time_score = self.sigmoid(duration, midpoint=4,   k=0.08 * k_factor, max_value=40)
            baseline = area_score + time_score
            scores.append(baseline)

        self._cleanup_lost_tracks()
        scores_arr = np.array(scores)
        weights = np.exp(scores_arr)  # softmax-like emphasis
        final_score = min(np.sum(weights * scores_arr) / np.sum(weights), self.max_score)

        return final_score, tracked


    def _cleanup_lost_tracks(self):
        now = time.time()
        remove_ids = [tid for tid, last in self.last_seen.items() if now - last > 1.0]
        for tid in remove_ids:
            self.first_seen.pop(tid, None)
            self.last_seen.pop(tid, None)

    def sigmoid(self, x, midpoint, k=0.12, max_value=100.0):
        return max_value / (1 + math.exp(-k * (x - midpoint)))