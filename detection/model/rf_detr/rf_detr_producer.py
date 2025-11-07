import pika
import uuid
import json
import time

class RFDETRProducer:
    def __init__(self, user, password, host, vhost):
        self.user = user
        self.password = password
        self.host = host
        self.vhost = vhost

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host, port=5672, virtual_host=self.vhost,
            credentials=pika.PlainCredentials(self.user, self.password)
        ))

        self.channel = self.connection.channel()

        # Declare the task queue (what we send TO the server)
        self.channel.queue_declare(queue="rf-detr-suspicion-task", durable=True)

        # Create a private, auto-delete queue to receive responses
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        # Set up consumer to listen for replies
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True
        )

        self.response = None
        self.correlation_id = None

    def _on_response(self, ch, method, props, body):
        # Only process the response that matches the original request ID
        if props.correlation_id == self.correlation_id:
            self.response = body.decode("utf-8")  # or JSON load if needed


    def send_frame(self, frame_bytes, timeout=5):
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
            self.connection.process_data_events()
            if time.time() - start > timeout:
                raise TimeoutError("RF-DETR server did not respond in time.")

        return self.response
