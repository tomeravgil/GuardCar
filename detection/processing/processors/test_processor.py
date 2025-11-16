import cv2
from detection.processing.processors.processor import Processor
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class VideoTestProcessor(Processor):
    """
    Offline video tester with color-separated graphs per video.
    """

    def __init__(self, local_detection_service, cloud_detection_service, tracking_service):
        super().__init__(local_detection_service, cloud_detection_service, tracking_service)

        # PER-VIDEO STORAGE
        self.video_results = []


    # -------------------------------------------------------------
    # REQUIRED IMPLEMENTATION OF ABSTRACT METHOD
    # -------------------------------------------------------------
    def start_video_processing(self, video_paths):
        """
        Main entrypoint. Accepts one video or a list of videos.
        """

        if isinstance(video_paths, str):
            video_paths = [video_paths]

        logger.info(f"[TEST] Running analysis on {len(video_paths)} video(s)")

        self.video_results = []  # reset

        for path in video_paths:
            self._process_single_video(path)

        self._generate_graphs(video_paths)


    # -------------------------------------------------------------
    # PROCESS ONE VIDEO
    # -------------------------------------------------------------
    def _process_single_video(self, video_path):
        logger.info(f"[TEST] Processing video: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video {video_path}")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_idx = 0

        timestamps = []
        scores = []
        areascores = []              # list of (area_ratio, score)
        class_timeline = defaultdict(list)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = frame_idx / fps
            resized = cv2.resize(frame, (640, 640))
            frame_bytes = cv2.imencode('.jpg', resized)[1].tobytes()

            score, tracked = self._apply_processing(frame_bytes, resized)

            timestamps.append(timestamp)
            scores.append(score)

            H, W = resized.shape[:2]
            for i in range(len(tracked)):
                x1, y1, x2, y2 = tracked.xyxy[i].astype(float)
                cls_id = int(tracked.class_id[i])
                cls_name = self.id_to_name.get(cls_id, "unknown")

                area_ratio = ((x2 - x1) * (y2 - y1)) / (W * H)

                class_timeline[cls_name].append(timestamp)
                areascores.append((area_ratio, score))

            frame_idx += 1

        cap.release()

        # Save results for this video
        self.video_results.append({
            "path": video_path,
            "timestamps": timestamps,
            "scores": scores,
            "class_timeline": class_timeline,
            "areascores": areascores
        })

        logger.info(f"[TEST] Completed video: {video_path}")


    # -------------------------------------------------------------
    # GRAPH GENERATION WITH MULTI-VIDEO COLORS
    # -------------------------------------------------------------
    def _generate_graphs(self, video_paths):
        logger.info("[TEST] Generating graphs...")

        colors = plt.cm.tab10(np.linspace(0, 1, len(self.video_results)))

        # -------- GRAPH 1: CLASS TIMELINE --------
        plt.figure(figsize=(14, 6))

        for color, video in zip(colors, self.video_results):
            for cls_name, times in video["class_timeline"].items():
                plt.scatter(times, [cls_name] * len(times), s=10, color=color,
                            label=f"{video['path']} – {cls_name}")

        plt.title("Class Appearance Timeline (Per Video)")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Class")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.legend(fontsize=8)
        plt.show()


        # -------- GRAPH 2: SUSPICION SCORE OVER TIME --------
        plt.figure(figsize=(14, 5))

        for color, video in zip(colors, self.video_results):
            plt.plot(video["timestamps"], video["scores"], color=color,
                     label=video["path"])

        plt.title("Suspicion Score Over Time (Per Video)")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Suspicion Score")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()


        # -------- GRAPH 3: AREA RATIO VS SCORE --------
        plt.figure(figsize=(10, 6))

        for color, video in zip(colors, self.video_results):
            if video["areascores"]:
                areas, scores = zip(*video["areascores"])
                plt.scatter(areas, scores, alpha=0.5, color=color,
                            label=video["path"])

        plt.title("Area Ratio vs Suspicion Score (Per Video)")
        plt.xlabel("Area Ratio (0–1)")
        plt.ylabel("Suspicion Score")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()

        logger.info("[TEST] Graphs created successfully.")
