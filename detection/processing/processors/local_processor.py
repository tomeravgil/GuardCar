import logging
from abc import abstractmethod

from detection.model.detection_service import DetectionService
from detection.processing.processors.processor import Processor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

class LocalProcessor(Processor):

    def __init__(self,detection_service: DetectionService, tracking_service):
        super().__init__(detection_service, tracking_service)

    def process(self, resized_frame, frame_id):
        detections = self.local_detection_service.detect(resized_frame)
        return self.tracking_service.process_detections(
            detections.detections,
            resized_frame.shape[:2]
        )