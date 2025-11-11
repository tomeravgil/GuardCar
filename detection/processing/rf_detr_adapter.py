from detection.model.rf_detr.rf_detr_producer import RFDETRProducer
import pybreaker
import logging
import json 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


class RFDETRRemoteServiceAdapter:
    """
    Adapter that wraps RFDETRProducer so it matches the .detect() signature
    expected by the Processor.
    """
    def __init__(self, producer: RFDETRProducer):
        self.producer = producer

    def detect(self, frame_bytes):
        """
        Send the frame to the remote RF-DETR server and wait for the response.
        The producer returns a string/JSON — if needed, parse into your
        detection result format here.
        """
        if self.producer is None:
            raise pybreaker.CircuitBreakerError("RF-DETR producer not initialized")

        response = self.producer.send_frame(frame_bytes)
        return self._parse_response(response)

    def _parse_response(self, response):
        # If response is already a list, return it
        if isinstance(response, list):
            return response
        
        # Otherwise, parse JSON string
        try:
            return json.loads(response)
        except Exception as e:
            logger.error(f"[RF-DETR Parse Error] Could not parse server response: {e}")
            return []