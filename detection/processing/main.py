#!/usr/bin/env python3

from detection.processing.adapters.cloud_model_adapter_base import CloudModelAdapter
from detection.processing.processor import Processor
from detection.model.yolo.yolo_detection import YOLODetectionService
from detection.model.cloud_model.producer.cloud_model_producer import CloudModelProducer
from detection.tracking.tracking_service import TrackingDetectionService
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    yolo_detection_service = YOLODetectionService(model_path="yolov8n.pt")
    cloud_producer = None
    try:
        cloud_producer = CloudModelProducer(
            user="tomer",
            password="yourpassword",
            host="192.168.1.68",
            vhost="/",
            model_name="rf-detr"
        )
    except Exception as e:
        logger.error(f"Failed to initialize RF-DETR producer: {e}")

    rf_detection_service = CloudModelAdapter(cloud_producer)

    tracking_service = TrackingDetectionService()

    processor = Processor(
        yolo_detection_service=yolo_detection_service,
        cloud_detection_service=rf_detection_service,
        tracking_service=tracking_service
    )

    processor.start_video_processing()


if __name__ == "__main__":
    main()
