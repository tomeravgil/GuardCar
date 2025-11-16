from detection.dto.detection_types import Detection, DetectionResult
from ultralytics import YOLO
from typing import Optional
from detection.model.detection_service import DetectionService
import cv2
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

class YOLODetectionService(DetectionService):
    def __init__(self, model_path: str):
        super().__init__(model_path)

    def load_model(self, model_path: Optional[str] = None):
        """Load a YOLO model from the specified path."""
        try:
            model = YOLO(model_path)
            logger.info(f"Successfully loaded YOLO model from {model_path}")
            return model
        except Exception as e:
            logger.error(f"Error loading YOLO model from {model_path}: {e}")
            return None
        
    def get_classes(self):
        return {name.lower(): idx for idx, name in self.model.names.items()}

    def detect(self, frame) -> DetectionResult:
        # Decode JPEG bytes if needed
        if isinstance(frame, (bytes, bytearray)):
            frame = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)

        # Run YOLO inference
        result = self.model.predict(frame, verbose=False)[0]
        
        detections = []
        names = self.model.names

        # Convert YOLO output into unified dataclass
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
            conf = float(box.conf.cpu().numpy())
            cls_id = int(box.cls.cpu().numpy())
            class_name = names[cls_id].lower()

            detections.append(
                Detection(
                    class_id=cls_id,
                    class_name=class_name,
                    confidence=conf,
                    bbox=[float(x1), float(y1), float(x2), float(y2)]
                )
            )

        # Wrap into DetectionResult object
        return DetectionResult(detections=detections)
