from detection.processing.adapters.cloud_model_adapter import CloudModelAdapter
from detection.processing.processors.test_processor import VideoTestProcessor
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


# ---------------------------------------------------------
# YOLO Model Download
# ---------------------------------------------------------
def ensure_yolo_model_exists(model_path: str):
    """Download YOLO model if missing."""
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


# ---------------------------------------------------------
# IP Validation
# ---------------------------------------------------------
def is_valid_ipv4(ip: str) -> bool:
    """Validate IPv4 format."""
    pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    if not re.match(pattern, ip):
        return False

    parts = ip.split(".")
    return all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)


def ask_for_ip() -> str:
    """Ask user for cloud IP and validate it."""
    ip = input("Enter the IP address of your cloud model: ").strip()

    if not ip:
        logger.error("No IP provided. Exiting.")
        sys.exit(1)

    if not is_valid_ipv4(ip):
        logger.error(f"Invalid IP address: {ip}")
        sys.exit(1)

    return ip


# ---------------------------------------------------------
# Video Path Input
# ---------------------------------------------------------
def ask_for_video_paths():
    """
    Ask user for comma-separated video paths.
    If empty input → return None (meaning: run with no video paths).
    """
    raw = input(
        "Enter video paths separated by commas (or press ENTER to run without videos): "
    ).strip()

    # Empty input -> run processing without videos
    if not raw:
        logger.info("No video paths provided. Running processor without videos.")
        return None

    # Split on comma, clean whitespace
    paths = [p.strip() for p in raw.split(",") if p.strip()]

    # Validate existence
    validated = []
    for p in paths:
        if not os.path.exists(p):
            logger.error(f"Video file does not exist: {p}")
            sys.exit(1)
        validated.append(p)

    return validated


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    # Ask for cloud IP
    cloud_ip = ask_for_ip()

    # Ensure YOLO model exists
    model_path = "yolov11n.pt"
    ensure_yolo_model_exists(model_path)

    # Load YOLO
    yolo_detection_service = YOLODetectionService(model_path=model_path)

    # Initialize cloud producer
    try:
        cloud_producer = CloudModelProducer(
            user="tomer",
            password="yourpassword",
            host=cloud_ip,
            vhost="/",
            model_name="rf-detr"
        )
    except Exception as e:
        logger.error(f"Failed to initialize RF-DETR producer: {e}")
        sys.exit(1)

    # Cloud + tracking + processor
    rf_detection_service = CloudModelAdapter(cloud_producer)
    tracking_service = TrackingDetectionService()

    processor = VideoTestProcessor(
        local_detection_service=yolo_detection_service,
        cloud_detection_service=rf_detection_service,
        tracking_service=tracking_service
    )

    # Ask user for video paths
    video_paths = ask_for_video_paths()

    # Start processing
    processor.start_video_processing(video_paths=video_paths)


if __name__ == "__main__":
    main()
