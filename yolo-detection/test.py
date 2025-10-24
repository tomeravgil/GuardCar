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

if __name__ == "__main__":
    model = "yolov8n.pt"        
    testVideofolder = "testVideos"    

    if not os.path.isdir(testVideofolder):
        raise FileNotFoundError(f"Folder '{TEST_VItestVideofolderDEO_DIR}' not found.")

    videoFiles = [
        os.path.join(testVideofolder, f)
        for f in os.listdir(testVideofolder)
        if f.lower().endswith(".mp4")
    ]

    if not videoFiles:
        raise FileNotFoundError(f"No files found in '{TEST_VIDEO_DIR}'")

    runner = VideoRunner(model)

    # 4. loop over each video
    for videoPath in videoFiles:
        print(f"\n===== Processing video: {videoPath} =====")

        frameScores = runner.run_on_video(videoPath)

        for i, score in enumerate(frameScores):
            print(f"Frame {i:04d} | Suspicion score: {score:.6f}")

        if frameScores:
            avgScore = sum(frameScores) / len(frameScores)
            maxScore = max(frameScores)
            minScore = min(frameScores)

            print("----- Summary -----")
            print(f"Frames processed: {len(frameScores)}")
            print(f"Avg suspicion score: {avgScore:.6f}")
            print(f"Max suspicion score: {maxScore:.6f}")
            print(f"Min suspicion score: {minScore:.6f}")
        else:
            print("No frames processed")