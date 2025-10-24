import os
import math
from typing import List
from detection_service import TrackingDetectionService


class VideoRunner:
    # initialize the class 
    def __init__(self, modelPath):
        self.service = TrackingDetectionService(modelPath, None)

    # get the suspision score of evrey frame 
    def run_on_video(self, videoPath):
        frame_scores = []

        for result in self.service.model.track(
            source=videoPath,
            stream=True,
            tracker=self.service.tracker
        ):
            score = self.service.handle_result(result)
            if score is None or (isinstance(score, float) and math.isnan(score)):
                score = 0.0
            frame_scores.append(score)

        return frame_scores