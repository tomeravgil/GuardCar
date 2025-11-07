#!/usr/bin/env python3

from detection.processing.processor import Processor
from detection.model.yolo.yolo_detection import YOLODetectionService
from detection.model.rf_detr.rf_detr_producer import RFDETRProducer
from detection.tracking.tracking_service import TrackingDetectionService

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
        response = self.producer.send_frame(frame_bytes)
        return self._parse_response(response)

    def _parse_response(self, response):
        """
        TODO: Convert RF-DETR remote response to YOLO-like output format.
        For now, return raw response (you can refine later).
        """
        return response


def main():
    # ---- YOLO fallback model ----
    yolo_detection_service = YOLODetectionService(model_path="yolov8n.pt")

    # ---- Remote RF-DETR (RabbitMQ) ----
    rfdetr_producer = RFDETRProducer(
        user="guest",
        password="guest",
        host="localhost",
        vhost="/"
    )
    rf_detection_service = RFDETRRemoteServiceAdapter(rfdetr_producer)

    # ---- Tracking ----
    tracking_service = TrackingDetectionService()

    # ---- Create Processor ----
    processor = Processor(
        yolo_detection_service=yolo_detection_service,
        rf_detection_service=rf_detection_service,
        tracking_service=tracking_service
    )

    # ---- Go! ----
    processor.start_video_processing()


if __name__ == "__main__":
    main()
