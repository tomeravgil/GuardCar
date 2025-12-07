import socket
import struct
import cv2
import numpy as np
import time
import asyncio
import logging
import os
import requests

from detection.model.yolo.yolo_detection import YOLODetectionService
from detection.processing.processors.local_processor import LocalProcessor
from detection.processing.processors.processor import Processor
from detection.tracking.tracking_service import TrackingDetectionService
from detection.processing.processors.rpc_processor import RPCProcessor
from detection.model.detection_service import DetectionService
from gRPC.grpc_client import CloudClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


# --------------------------
# Utilities
# --------------------------
def receive_all(sock, length):
    """Receive exactly `length` bytes from socket."""
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data


def ensure_yolo_model_exists(model_path: str):
    """Ensures YOLO model exists, downloads if missing."""
    if os.path.exists(model_path):
        return

    url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt"
    logger.info(f"Downloading YOLO model from {url}")

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(model_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    logger.info(f"Downloaded YOLO model to {model_path}")


# --------------------------
# Main Combined Class
# --------------------------
class StreamRPCClient:
    def __init__(self, processor: Processor):
        self.rpc = processor

    async def connect_and_process(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info(f"Connecting to {ip}:{port} ...")

        try:
            s.connect((ip, port))
            logger.info("Connected! Receiving stream...")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return

        frame_id = 0
        prev_time = time.time()

        try:
            while True:
                # 1. Read frame header
                header = receive_all(s, 4)
                if not header:
                    logger.warning("Stream ended.")
                    break

                frame_len = struct.unpack("!I", header)[0]

                # 2. Read JPEG payload
                jpg_bytes = receive_all(s, frame_len)
                if jpg_bytes is None:
                    logger.warning("Lost frame.")
                    break

                # 3. Decode JPEG → OpenCV
                img = cv2.imdecode(np.frombuffer(jpg_bytes, np.uint8), cv2.IMREAD_COLOR)
                if img is None:
                    continue

                # 5. Run RPCProcessor (local+cloud+tracking)
                score, tracked = self.rpc.process(resized_frame=img, frame_id=frame_id)

                # 6. Draw detections
                for i in range(len(tracked)):
                    x1, y1, x2, y2 = tracked.xyxy[i].astype(int)

                    cls_id = int(tracked.class_id[i])
                    track_id = int(tracked.tracker_id[i])

                    cls_name = self.rpc.get_classification(cls_id)
                    logger.info(f"tracked {cls_name}")
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
                    cv2.putText(img, f"{cls_name} #{track_id}",
                                (x1, y1 - 8),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0,255,0), 2)

                # 7. FPS display
                now = time.time()
                fps = 1.0 / (now - prev_time)
                prev_time = now
                frame_id += 1

                cv2.putText(img, f"FPS: {fps:.1f}  Score: {score:.2f}",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0,255,255), 2)

                # 8. Display window
                cv2.imshow("GuardCar RPC Stream", img)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            logger.info("Interrupted.")

        finally:
            s.close()
            cv2.destroyAllWindows()
            logger.info("Stream closed.")


# --------------------------
# Main Entry
# --------------------------
async def main():
    ip = input("Enter Raspberry Pi IP: ")
    port = int(input("Enter port (8443): ") or 8443)

    # YOLO model
    model_path = "yolo11n.pt"
    ensure_yolo_model_exists(model_path)
    yolo = YOLODetectionService(model_path)

    tracking = TrackingDetectionService()

    localProcessor = LocalProcessor(detection_service=yolo, tracking_service=tracking)


    # Run streaming + RPC pipeline
    client = StreamRPCClient(localProcessor)
    await client.connect_and_process(ip, port)


if __name__ == "__main__":
    asyncio.run(main())
