import asyncio
from detection.model.detection_service import DetectionService
from circuitbreaker import circuit, CircuitBreaker, CircuitBreakerError, CircuitBreakerMonitor
import logging
from detection.processing.processors.processor import Processor
from detection.tracking.tracking_service import TrackingDetectionService
from gRPC.grpc_client import CloudClient
from detection.dto.detection_types import DetectionResult, Detection
from time import monotonic
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

def _convert_rpc_dr_to_internal_dr(rpc_detection_result) -> DetectionResult:
    detections = []
    for detection in rpc_detection_result.detections:
        new_detection = Detection(
            class_id=detection.class_id,
            class_name=detection.class_name,
            confidence=detection.confidence,
            bbox=[detection.x1, detection.y1, detection.x2, detection.y2]
        )
        detections.append(new_detection)
    return DetectionResult(detections=detections)

class RPCProcessor(Processor):
    def __init__(self,
                 local_detection_service: DetectionService,
                 cloud_client: CloudClient,
                 tracking_service: TrackingDetectionService):
        super().__init__(local_detection_service=local_detection_service,
                         tracking_service=tracking_service)
        self.cloud_client = cloud_client

    async def process(self, resized_frame, frame_id):
        try:
            # Protected (breaker-wrapped) cloud calls
            if CircuitBreakerMonitor.get("RPCProcessor._cloud_result").state == "half_open":
                await self._cloud_reconnect()
            cloud_result = await self._cloud_result(resized_frame,frame_id)

            if cloud_result is None:
                raise Exception("Cloud Model timed out")

            cloud_result = _convert_rpc_dr_to_internal_dr(cloud_result[0])

            # Map class ids
            for detection in cloud_result.detections:
                class_name = detection.class_name.lower()
                cls_id = self.class_map.get(class_name)
                if cls_id is not None:
                    detection.class_id = cls_id

            detections = cloud_result

        except CircuitBreakerError:
            # Cloud died or breaker is open → fallback
            logger.warning(f"Cloud unavailable, falling back to Local Model")
            future = asyncio.run_coroutine_threadsafe(
                self.cloud_client.clear_queue(),
                self.cloud_client.loop
            )
            await asyncio.wrap_future(future)
            detections = self.local_detection_service.detect(resized_frame)
        except Exception as e:
            # Unexpected cloud error → fallback
            logger.error(f"Unexpected Cloud Model error: {e}")
            future = asyncio.run_coroutine_threadsafe(
                self.cloud_client.clear_queue(),
                self.cloud_client.loop
            )
            await asyncio.wrap_future(future)
            detections = self.local_detection_service.detect(resized_frame)

        # Run tracking
        return self.tracking_service.process_detections(
            detections.detections,
            resized_frame.shape[:2]
        )

    @circuit(cls=CircuitBreaker, recovery_timeout=5)
    async def _cloud_result(self, resized_frame, frame_id):
        # Schedule send_frame on the main loop (where CloudClient lives)
        future_send = asyncio.run_coroutine_threadsafe(
            self.cloud_client.send_frame(resized_frame, frame_id),
            self.cloud_client.loop
        )
        await asyncio.wrap_future(future_send)

        # Schedule get_processed_frame on the main loop
        future_get = asyncio.run_coroutine_threadsafe(
            self.cloud_client.get_processed_frame(frame_id=frame_id, timeout=1),
            self.cloud_client.loop
        )
        return await asyncio.wrap_future(future_get)

    async def _cloud_reconnect(self):
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.cloud_client.connected.wait(),
                self.cloud_client.loop
            )
            # wait_for needs to wrap the future
            await asyncio.wait_for(asyncio.wrap_future(future), timeout=1.0)
        except asyncio.TimeoutError:
            pass

    async def stop(self):
        await self.cloud_client.stop()
