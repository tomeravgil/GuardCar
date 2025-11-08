import pika
import uuid
import time

class RFDETRProducer:
    def __init__(self, user, password, host, vhost):
        self.user = user
        self.password = password
        self.host = host
        self.vhost = vhost

        self.response = None
        self.correlation_id = None

        self._connect()

    def _on_response(self, ch, method, props, body):
        # Only process the response that matches the original request ID
        if props.correlation_id == self.correlation_id:
            self.response = body.decode("utf-8")


    def send_frame(self, frame_bytes, timeout=.5):
        try:
            return self._send_frame_internal(frame_bytes, timeout)
        except (pika.exceptions.AMQPError, ConnectionError, OSError):
            print("[RF-DETR] Lost RabbitMQ connection. Reconnecting...")
            try:
                if not self._is_connected():
                    self._connect()
                    if not self._is_connected():
                        raise Exception("Failed to reconnect to RabbitMQ")
                return self._send_frame_internal(frame_bytes, timeout)
            except Exception as e:
                print("[RF-DETR] Reconnect failed.")
                raise e


    def _send_frame_internal(self, frame_bytes, timeout):
        self.response = None
        self.correlation_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange="",
            routing_key="rf-detr-suspicion-task",
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.correlation_id,
            ),
            body=frame_bytes
        )

        start = time.time()
        while self.response is None:
            self.connection.process_data_events(time_limit=0.1)
            if time.time() - start > timeout:
                raise TimeoutError("RF-DETR server did not respond in time.")

        return self.response

    def _connect(self):
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

        # Declare the queues again because new channel ≠ old channel
        self.channel.queue_declare(queue="rf-detr-suspicion-task", durable=True)

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True
        )

    def _is_connected(self):
        return self.connection and not self.connection.is_closed