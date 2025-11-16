from detection.processing.adapters.cloud_model_adapter import CloudModelAdapter
from detection.processing.processors.demo_processor import DemoProcessor
from detection.model.yolo.yolo_detection import YOLODetectionService
from detection.model.cloud_model.producer.cloud_model_producer import CloudModelProducer
from detection.tracking.tracking_service import TrackingDetectionService
import logging
import os
import requests
import re
import sys

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


def is_valid_ipv4(ip: str) -> bool:
    """Return True if the string is a valid IPv4 address."""
    pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    if not re.match(pattern, ip):
        return False

    parts = ip.split(".")
    return all(0 <= int(p) <= 255 for p in parts)


def ask_for_ip() -> str:
    """Ask the user for an IP address and validate it."""
    ip = input("Enter the IP address of your cloud model: ").strip()

    if not ip:
        logger.error("No IP provided. Exiting.")
        sys.exit(1)

    if not is_valid_ipv4(ip):
        logger.error(f"Invalid IP address: {ip}")
        sys.exit(1)

    return ip


def main():
    # Ask user for cloud IP
    cloud_ip = ask_for_ip()

    model_path = "yolo11n.pt"

    # Ensure model exists (download if needed)
    ensure_yolo_model_exists(model_path)

    # Load YOLO
    yolo_detection_service = YOLODetectionService(model_path=model_path)

    # Try Cloud producer
    try:
        cloud_producer = CloudModelProducer(
            user="guardcar",
            password="guardcar",
            host=cloud_ip,
            vhost="/",
            model_name="rf-detr"
        )
    except Exception as e:
        logger.error(f"Failed to initialize RF-DETR producer: {e}")
        sys.exit(1)

    rf_detection_service = CloudModelAdapter(cloud_producer)

    tracking_service = TrackingDetectionService()

    processor = DemoProcessor(
        local_detection_service=yolo_detection_service,
        cloud_detection_service=rf_detection_service,
        tracking_service=tracking_service
    )

    processor.start_video_processing()


if __name__ == "__main__":
    main()
