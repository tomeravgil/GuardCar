from detection.model.yolo.yolo_detection import YOLODetectionService
from detection.tracking.tracking_service import TrackingDetectionService
import os
import requests
import cv2
from detection.model.detection_service import DetectionService
from detection.processing.processors.rpc_processor import RPCProcessor
import time
import logging
import asyncio
from gRPC.grpc_client import CloudClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


def ensure_yolo_model_exists(model_path: str):
    """Ensures YOLO model exists, downloads if missing."""
    if os.path.exists(model_path):
        return

    url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt"
    logger.info(f"YOLO model not found. Downloading from {url}")

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(model_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    logger.info(f"YOLO model downloaded to {model_path}")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

class Demo:
    """
    Class to Demo the Cloud Detection Service and Local Detection Service working together.
    """

    def __init__(self, local_detection_service: DetectionService, cloud_detection_service, tracking_service):
        self.processor = RPCProcessor(local_detection_service,cloud_detection_service,tracking_service)

    async def start_video(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            logger.error("Error: Could not open camera.")
            return

        logger.info("Starting video capture. Press 'q' to quit...")
        prev_time = time.time()
        frame_id = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Resize feed for model inputs
                resized = cv2.resize(frame, (640, 640))
                score, tracked = await self.processor.process(resized_frame=resized, frame_id=frame_id)
                for i in range(len(tracked)):
                    x1, y1, x2, y2 = tracked.xyxy[i].astype(int)
                    cls_id = int(tracked.class_id[i])
                    track_id = int(tracked.tracker_id[i])

                    cls_name = self.processor.get_classification(cls_id)

                    cv2.rectangle(resized, (x1, y1), (x2, y2), (0,255,0), 2)
                    cv2.putText(resized, f"{cls_name} #{track_id}",
                                (x1, y1 - 8),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0,255,0), 2)

                # FPS
                current_time = time.time()
                fps = 1 / (current_time - prev_time)
                prev_time = current_time
                frame_id += 1
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


async def main():

    model_path = "yolo11n.pt"

    # Ensure model exists (download if needed)
    ensure_yolo_model_exists(model_path)

    # Load YOLO
    yolo_detection_service = YOLODetectionService(model_path=model_path)

    cert_path = "gRPC/server.crt"
    server = "localhost:50051"
    # Try Cloud producer
    try:
        cloud_producer = CloudClient(server, cert_path)
    except Exception as e:
        logger.error(f"Failed to initialize cloud producer: {e}")
        cloud_producer = None

    tracking_service = TrackingDetectionService()

    processor = Demo(
    local_detection_service=yolo_detection_service,
    cloud_detection_service=cloud_producer,
    tracking_service=tracking_service
    )

    if cloud_producer is not None:
        asyncio.create_task(cloud_producer.start())
        logger.info("Waiting for gRPC connection...")
        try:
            await asyncio.wait_for(cloud_producer.connected.wait(), timeout=5.0)
            logger.info("gRPC connected!")
        except asyncio.TimeoutError:
            logger.warning("gRPC connection timed out. Proceeding, but cloud features may be unavailable.")

    await processor.start_video()



if __name__ == "__main__":
    asyncio.run(main())
