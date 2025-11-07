from rf_detr_consumer import RFDETRConsumer
from rf_detr_detection import RFDETRDetectionService

if __name__ == "__main__":
    detection_service = RFDETRDetectionService("rfdetr-base")
    consumer = RFDETRConsumer("guest", "guest", "localhost", "/", detection_service)
    consumer.connect()
    consumer.start()