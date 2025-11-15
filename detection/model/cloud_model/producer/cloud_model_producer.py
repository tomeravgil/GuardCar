import pika
import uuid
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

class CloudModelProducer:
    """
    Sends frames to a model-specific RabbitMQ task queue and waits for a
    response using RPC-style correlation IDs and a temporary callback queue.
    Handles reconnection logic when RabbitMQ becomes unavailable.
    """

    def __init__(self, user, password,host, vhost, model_name):
        self.user = user
        self.password = password
        self.host = host
        self.vhost = vhost
        self.model_name = model_name
        self.response = None
        self.correlation_id = None

        self._connect()

    def _on_response(self, ch, method, props, body):
        """
        Callback triggered whenever the model sends back a result.
        Only accept the message if the correlation_id matches the one we sent.
        """

        # Only process the response that matches the original request ID
        if props.correlation_id == self.correlation_id:
            self.response = body
        
    def send_frame(self, frame_bytes, timeout=.5):
        """
        Sends a frame to the suspicion-task queue and waits synchronously
        for a response. Includes automatic reconnection if RabbitMQ dropped.
        """

        try:
            return self._rpc_frame_internal(frame_bytes, timeout)
        except (pika.exceptions.AMQPError, ConnectionError, OSError):
            logger.error(f"[{self.model_name}] Lost RabbitMQ connection. Reconnecting...")
            try:
                if not self._is_connected():
                    self._connect()
                    if not self._is_connected():
                        raise Exception("Failed to reconnect to RabbitMQ")
                return self._rpc_frame_internal(frame_bytes, timeout)
            except Exception as e:
                logger.error(f"[{self.model_name}] Reconnect failed.")
                raise e

    def _rpc_frame_internal(self, frame_bytes, timeout):
        """
        Internal implementation of the RPC frame send.
        Publishes the frame with correlation_id and waits for a matching response.
        """

        self.response = None

        self.send_frame(frame_bytes=frame_bytes)

        self._receive_frame(timeout=timeout)

        return self.response

    def _send_frame(self, frame_bytes):
        """
        Internal helper to send the frame
        """
        self.correlation_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange="",
            routing_key=f"{self.model_name.lower().replace(' ','-')}-suspicion-task",
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.correlation_id,
            ),
            body=frame_bytes
        )

    def _receive_frame(self, timeout):
        """
        Internal helper to receive the frame
        """

        start = time.time()
        while self.response is None:
            self.connection.process_data_events(time_limit=0.1)
            if time.time() - start > timeout:
                raise TimeoutError(f"{self.model_name} server did not respond in time.")

    def _connect(self):
        """
        Creates a RabbitMQ BlockingConnection, declares queues, and initializes
        a private exclusive callback queue used for RPC responses.
        """

        credentials = pika.PlainCredentials(self.user, self.password)
        params = pika.ConnectionParameters(
            host=self.host,
            port=5672,
            virtual_host=self.vhost,
            credentials=credentials,
            heartbeat=30, 
            blocked_connection_timeout=60
        )

        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()

        # Declare the queues again because new channel != old channel
        self.channel.queue_declare(queue=f"{self.model_name.lower().replace(' ','-')}-suspicion-task", durable=True)

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True
        )
    
    def _is_connected(self):
        """
        Returns True if the connection exists and is still open.
        """
        
        return self.connection and not self.connection.is_closed