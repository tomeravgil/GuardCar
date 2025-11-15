import cv2
from detection.model.detection_service import DetectionService
from detection.processing.processors.processor import Processor
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

class DemoProcessor(Processor):
    """
    Extension Class to Demo the Cloud Detection Service and Local Detection Service working together.
    """

    def __init__(self, local_detection_service: DetectionService, cloud_detection_service, tracking_service):
        super.__init__(local_detection_service,cloud_detection_service,tracking_service)

    def start_video_processing(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            logger.error("Error: Could not open camera.")
            return

        logger.info("Starting video capture. Press 'q' to quit...")
        prev_time = time.time()

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Resize feed for model inputs
                resized = cv2.resize(frame, (640, 640))
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                frame_bytes = cv2.imencode('.jpg', gray)[1].tobytes()

                score, tracked = self._apply_processing(frame_bytes=frame_bytes, resized_frame=resized)
                for i in range(len(tracked)):
                    x1, y1, x2, y2 = tracked.xyxy[i].astype(int)
                    cls_id = int(tracked.class_id[i])
                    track_id = int(tracked.tracker_id[i])

                    cls_name = self.id_to_name.get(cls_id, "obj")

                    cv2.rectangle(resized, (x1, y1), (x2, y2), (0,255,0), 2)
                    cv2.putText(resized, f"{cls_name} #{track_id}",
                                (x1, y1 - 8),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0,255,0), 2)

                # FPS
                current_time = time.time()
                fps = 1 / (current_time - prev_time)
                prev_time = current_time

                cv2.putText(resized, f"FPS: {fps:.1f} Score: {score:.2f}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 255, 255), 2)

                cv2.imshow("Camera Feed", resized)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()
            logger.info("Video stream stopped and resources released.")
