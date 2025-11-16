from detection.processing.adapters.cloud_model_adapter import CloudModelAdapter
from detection.processing.processors.processor import Processor
from detection.model.yolo.yolo_detection import YOLODetectionService
from detection.model.cloud_model.producer.cloud_model_producer import CloudModelProducer
from detection.processing.processors.test_processor import VideoTestProcessor
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
            host="YOUR_IP",
            vhost="/",
            model_name="rf-detr"
        )
    except Exception as e:
        logger.error(f"Failed to initialize RF-DETR producer: {e}")

    rf_detection_service = CloudModelAdapter(cloud_producer)

    tracking_service = TrackingDetectionService()

    processor = VideoTestProcessor(
        local_detection_service=yolo_detection_service,
        cloud_detection_service=rf_detection_service,
        tracking_service=tracking_service
    )

    videos = [
        "/Users/tomeravgil/Downloads/videos/IMG_0269.mp4",
        "/Users/tomeravgil/Downloads/videos/IMG_0270.mp4",
        "/Users/tomeravgil/Downloads/videos/IMG_0271.mp4"
    ]
    processor.start_video_processing(video_paths=videos)


if __name__ == "__main__":
    main()
