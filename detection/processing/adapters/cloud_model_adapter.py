from detection.dto.detection_types import Detection, DetectionResult
import logging
import json

from detection.model.cloud_model.producer.cloud_model_producer import CloudModelProducer 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


class CloudModelAdapter:
    """
    Base adapter class for remote cloud-based detection models.
    
    This class standardizes the interface so that all remote models behave like 
    local detectors: they expose a clean `.detect(frame_bytes)` method.
    
    The actual network transport (RabbitMQ, HTTP, gRPC, etc.) is handled by a 
    producer object injected into the adapter. The adapter is responsible only 
    for:
        - sending the frame to the producer
        - receiving the raw response
        - parsing it into a unified detection output format
    
    Subclasses must implement `parse_response()` to convert model-specific 
    responses (JSON, lists, strings, etc.) into whatever structure the 
    Processor expects.
    """

    def __init__(self, producer: CloudModelProducer):
        """
        Store the underlying producer that handles network communication.
        
        producer: An object exposing `send_frame(frame_bytes)`.
                  Can be CloudModelProducer or any future transport layer.
        """
        self.producer = producer

    def _parse_response(self, response):
        """
        Convert raw bytes returned from CloudModelProducer into a DetectionResult.
        """

        try:
            # Response is RAW BYTES → convert to dict
            data = json.loads(response.decode("utf-8"))
        except Exception as e:
            logger.error(f"[Cloud Model Parse Error] Could not parse server response: {e}")
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
                logger.error(f"[Cloud Model Parse Error] Bad detection entry: {e}")

        return DetectionResult(detections=detections)

    def detect(self, frame_bytes):
        """
        Unified detection call used by the Processor.
        
        Steps:
            1. Ensure the producer exists
            2. Send the frame to the remote model via producer.send_frame()
            3. Parse the remote models raw output using parse_response()
        
        Returns:
            Parsed model detections in a consistent format.
        """
        if self.producer is None:
            raise RuntimeError("Producer not available")

        # Send the raw frame to the remote model (RPC call or similar)
        response = self.producer.send_frame(frame_bytes)

        # Convert model-specific response into processor-ready format
        return self._parse_response(response)
