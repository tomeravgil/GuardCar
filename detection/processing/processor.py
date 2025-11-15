import cv2
import pybreaker
import time
import logging
from detection.processing.backoff_listener import ExponentialBackoffListener

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


# TODO split this into demo and non demo
class Processor:
    def __init__(self, yolo_detection_service, cloud_detection_service, tracking_service):
        self.yolo_detection_service = yolo_detection_service
        self.cloud_detection_service = cloud_detection_service
        self.tracking_service = tracking_service

        self.circuit_breaker = pybreaker.CircuitBreaker(
            fail_max=3,
            reset_timeout=5
        )
        self.circuit_breaker.add_listener(ExponentialBackoffListener(
            base_timeout=5,
            factor=2.0,
            max_timeout=120
        ))

        # YOLO class -> id map
        self.class_map = self.yolo_detection_service.get_classes()
        self.id_to_name = {v: k for k, v in self.class_map.items()}

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
                frame_bytes = cv2.imencode('.jpg', resized)[1].tobytes()

                # Try Cloud Model first
                try:
                    cloud_result = self.circuit_breaker.call(
                        self.cloud_detection_service.detect,
                        frame_bytes
                    )

                    # Convert Cloud Model → unified format
                    detections = cloud_result.detections
                except pybreaker.CircuitBreakerError:
                    # RF timed out so fallback to YOLO
                    detections = self.yolo_detection_service.detect(resized)
                except Exception as e:
                    # RF crashed so fallback to YOLO safely
                    logger.error(f"RF-DETR error: {e}, falling back to YOLO")
                    detections = self.yolo_detection_service.detect(resized)

                # ---- Run Tracking (adds track_id internally) ----
                score, tracked = self.tracking_service.process_detections(detections.detections, resized.shape[:2])

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
