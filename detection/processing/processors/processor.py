from detection.model.detection_service import DetectionService
import logging
from abc import ABC, abstractmethod

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

class Processor(ABC):
    def __init__(self, local_detection_service: DetectionService, tracking_service):
        self.local_detection_service = local_detection_service
        self.tracking_service = tracking_service

        # YOLO class -> id map
        self.class_map = self.local_detection_service.get_classes()
        self.id_to_name = {v: k for k, v in self.class_map.items()}

    @abstractmethod
    def process(self, resized_frame, frame_id):
        pass

    def get_classification(self, cls_id):
        return self.id_to_name.get(cls_id, "obj")