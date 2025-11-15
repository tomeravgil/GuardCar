from detection.dto.detection_types import Detection, DetectionResult
from detection.model.cloud_model.producer.cloud_model_producer import CloudModelProducer
from detection.processing.adapters.cloud_model_adapter_base import CloudModelAdapterBase
import logging
import json 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


class RFDETRRemoteServiceAdapter(CloudModelAdapterBase):
    """
    Adapter that wraps RFDETRProducer so it matches the .detect() signature
    expected by the Processor.
    """
    def __init__(self, producer: CloudModelProducer):
        self.producer = producer

    def _parse_response(self, response):
        """
        Convert raw bytes returned from CloudModelProducer into a DetectionResult.
        """

        try:
            # Response is RAW BYTES → convert to dict
            data = json.loads(response.decode("utf-8"))
        except Exception as e:
            logger.error(f"[RF-DETR Parse Error] Could not parse server response: {e}")
            return DetectionResult(detections=[])

        detections = []

        # Expect format:
        if "detections" not in data:
            logger.error("[Cloud Model Parse Error] Missing 'detections' field")
            return DetectionResult(detections=[])

        for det in data["detections"]:
            try:
                detection = Detection(
                    class_id=det["class_id"],
                    class_name=det["class_name"],
                    confidence=float(det["confidence"]),
                    bbox=det["bbox"]
                )
                detections.append(detection)

            except Exception as e:
                logger.error(f"[Cloud Parse Error] Bad detection entry: {e}")

        return DetectionResult(detections=detections)