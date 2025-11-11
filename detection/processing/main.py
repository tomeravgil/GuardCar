#!/usr/bin/env python3

from detection.processing.processor import Processor
from detection.model.yolo.yolo_detection import YOLODetectionService
from detection.model.rf_detr.rf_detr_producer import RFDETRProducer
from detection.tracking.tracking_service import TrackingDetectionService
from detection.processing.rf_detr_adapter import RFDETRRemoteServiceAdapter
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    yolo_detection_service = YOLODetectionService(model_path="yolov8n.pt")
    rfdetr_producer = None
    try:
        rfdetr_producer = RFDETRProducer(
            user="tomer",
            password="yourpassword",
            host="192.168.1.68",
            vhost="/"
        )
    except Exception as e:
        logger.error(f"Failed to initialize RF-DETR producer: {e}")

    rf_detection_service = RFDETRRemoteServiceAdapter(rfdetr_producer)

    tracking_service = TrackingDetectionService()

    processor = Processor(
        yolo_detection_service=yolo_detection_service,
        rf_detection_service=rf_detection_service,
        tracking_service=tracking_service
    )

    processor.start_video_processing()


if __name__ == "__main__":
    main()
