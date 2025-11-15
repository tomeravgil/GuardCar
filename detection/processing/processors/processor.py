from detection.model.detection_service import DetectionService
import pybreaker
import logging
from detection.processing.backoff_listener import ExponentialBackoffListener
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

class Processor(ABC):
    def __init__(self, local_detection_service: DetectionService, cloud_detection_service, tracking_service):
        self.local_detection_service = local_detection_service
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
        self.class_map = self.local_detection_service.get_classes()
        self.id_to_name = {v: k for k, v in self.class_map.items()}

    @abstractmethod
    def start_video_processing(self):
        pass

    def _apply_processing(self, frame_bytes, resized_frame):
        # Try Cloud Model first
        try:
            cloud_result = self.circuit_breaker.call(
                self.cloud_detection_service.detect,
                frame_bytes
            )
            for detection in cloud_result.detections:
                class_name = detection.class_name.lower()
                cls_id = self.class_map.get(class_name)
                if cls_id is None:
                    continue
                detection.class_id = cls_id
            # Convert Cloud Model to unified format
            detections = cloud_result
        except pybreaker.CircuitBreakerError:
            # Cloud Model timed out so fallback to Local
            detections = self.local_detection_service.detect(resized_frame)
        except Exception as e:
            # Cloud Model crashed so fallback to Local safely
            logger.error(f"Cloud Model error: {e}, falling back to Local Model")
            detections = self.local_detection_service.detect(resized_frame)

        # ---- Run Tracking (adds track_id internally) ----
        return self.tracking_service.process_detections(detections.detections, resized_frame.shape[:2])
