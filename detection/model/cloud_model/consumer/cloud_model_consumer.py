import pika
import json
import logging
from dataclasses import asdict
from detection.dto.detection_types import DetectionResult
from detection.model.detection_service import DetectionService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

class CloudModelConsumer:
    """
    Base class for consuming model-related tasks from RabbitMQ and producing results.
    Subclasses must implement `on_message` to define custom message handling logic.
    """

    def __init__(self: str, 
                 user: str, 
                 password: str, 
                 host: str, 
                 vhost: str, 
                 detection_service: DetectionService,
                 model_name: str):
        self.user = user
        self.password = password
        self.host = host
        self.vhost = vhost
        self.connection = None
        self.consume_channel = None
        self.produce_channel = None
        self.detection_service = detection_service
        self.model_name = model_name

    def connect(self):
        """
        Establish a connection to RabbitMQ and declare both consumption and 
        production queues. Queue names are derived from the model name.
        """

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host, port=5672, virtual_host=self.vhost,
            credentials=pika.PlainCredentials(self.user, self.password)
        ))
        self.consume_channel = self.connection.channel()
        self.consume_channel.queue_declare(queue=f"{self.model_name.lower().replace(' ','-')}-suspicion-task", durable=True)
        self.produce_channel = self.connection.channel()
        self.produce_channel.queue_declare(queue=f"{self.model_name.lower().replace(' ','-')}-suspicion-result", durable=True)
        logger.info("Connected to RabbitMQ and declared queues")

    def on_message(self, channel, method, properties, body):
        """
        Handle incoming messages from the suspicion-task queue.
        Must be implemented by subclasses depending on the model behavior.
        """
        # Run inference on incoming frame bytes
        result = self.detection_service.detect(body)
        
        if not isinstance(result, DetectionResult):
            raise TypeError("Expected DetectionResult from detection_service.detect()")

        # Serialize dataclass → dict → json
        json_body = json.dumps(asdict(result)).encode("utf-8")

        # Send reply back to requester
        self.produce_channel.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=json_body
        )

        channel.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        """
        Begin consuming messages from RabbitMQ. The consumer uses manual acknowledgements
        and limits unacknowledged messages with prefetch_count=1.
        """

        self.consume_channel.basic_qos(prefetch_count=1)
        self.consume_channel.basic_consume(
                                            queue=f"{self.model_name.lower().replace(' ', '-')}-suspicion-task", 
                                            on_message_callback=self.on_message, 
                                            auto_ack=False)
        try:
            self.consume_channel.start_consuming()
        except KeyboardInterrupt:
            self.consume_channel.stop_consuming()
            self.connection.close()
            logger.info("Consumer stopped.")