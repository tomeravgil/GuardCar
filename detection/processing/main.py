#!/usr/bin/env python3

from detection.processing.processor import Processor
from detection.model.yolo.yolo_detection import YOLODetectionService
from detection.model.rf_detr.rf_detr_producer import RFDETRProducer
from detection.tracking.tracking_service import TrackingDetectionService
import pybreaker

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
        return response


def main():
    yolo_detection_service = YOLODetectionService(model_path="yolov8n.pt")

    rfdetr_producer = None
    try:
        rfdetr_producer = RFDETRProducer(
            user="tomer",
            password="123",
            host="192.168.1.68",
            vhost="/"
        )
    except Exception as e:
        print(f"Failed to initialize RF-DETR producer: {e}")

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
