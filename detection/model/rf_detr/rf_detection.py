from detection.dto.detection_types import Detection, DetectionResult
from ..detection_service import DetectionService
from inference.models.utils import get_model
from typing import Optional
import torch

class RFDETRDetectionService(DetectionService):
    def __init__(self, model_path: str):
        self.model = get_model(
            model_path,
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
        )

    def load_model(self, model_path: Optional[str] = None):
        """Load a RFDETR model from the specified path."""
        pass
        
    def detect(self, frame) -> DetectionResult:
        """
        Run RF-DETR inference and convert results into a unified DetectionResult.

        The Processor expects DetectionResult(detections=[Detection...]).
        """
        inference_result = self.model.infer(frame, confidence=0.5)[0]

        detections = []

        for pred in inference_result.predictions:
            cx = pred.x
            cy = pred.y
            w  = pred.width
            h  = pred.height

            # Convert from center-x, center-y, w, h → xyxy
            x1 = cx - w / 2
            y1 = cy - h / 2
            x2 = cx + w / 2
            y2 = cy + h / 2

            det = Detection(
                class_id   = None,
                class_name = pred.class_name,
                confidence = float(pred.confidence),
                bbox       = [x1, y1, x2, y2],
            )

            detections.append(det)

        return DetectionResult(detections=detections)