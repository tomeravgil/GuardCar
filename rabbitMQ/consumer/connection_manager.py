import pika
import logging
import json
import threading
log = logging.getLogger(__name__)


class Producer:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        self.channel = None

    def get_queue(self):
        return self.queue_name

    def publish(self, message_obj, expire_time=None):
        if self.channel is None:
            log.error("Producer channel not ready yet!")
            return

        properties = pika.BasicProperties()
        if expire_time is not None:
            properties = pika.BasicProperties(
                expiration=expire_time,  # Message expires after 60 seconds (60000 milliseconds)
            )
        payload = json.dumps(message_obj.__dict__).encode()
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=payload,
            properties=properties
        )


class Consumer:
    def __init__(self, queue_name, event_queue, data_class):
        self.queue_name = queue_name
        self.event_queue = event_queue
        self.channel = None
        self.data_class = data_class
        self.asyncio_loop = None

    def get_queue(self):
        return self.queue_name

    def on_message(self, ch, method, props, body):
        try:
            data = json.loads(body.decode())
            msg = self.data_class(**data)

            # Push into async queue safely
            self.asyncio_loop.call_soon_threadsafe(
                self.event_queue.put_nowait, msg
            )
        except json.decoder.JSONDecodeError:
            log.error("Failed to decode JSON, ignoring")

        # Acknowledge
        ch.basic_ack(method.delivery_tag)

class ConnectionManager:
    def __init__(self, amqp_url, asyncio_loop=None):
        self.amqp_url = amqp_url
        self.connection = None
        self.consumers = []
        self.producers = []
        self.asyncio_loop = asyncio_loop

    def add_consumer(self, consumer):
        self.consumers.append(consumer)

    def add_producer(self, producer):
        self.producers.append(producer)

    def connect(self):
        return pika.SelectConnection(
            pika.URLParameters(self.amqp_url),
            on_open_callback=self.on_connection_open,
            on_close_callback=self.on_connection_closed,
        )

    def on_connection_open(self, connection):
        log.info("Connection opened")

        # Producers
        for producer in self.producers:
            connection.channel(
                on_open_callback=lambda ch, p=producer: self.on_producer_channel_open(ch, p)
            )

        # Consumers
        for consumer in self.consumers:
            consumer.asyncio_loop = self.asyncio_loop
            connection.channel(
                on_open_callback=lambda ch, c=consumer: self.on_consumer_channel_open(ch, c)
            )

    def on_producer_channel_open(self, channel, producer):
        log.info(f"Producer channel opened for queue: {producer.get_queue()}")
        producer.channel = channel

        # Declare queue safely (idempotent)
        channel.queue_declare(
            queue=producer.get_queue(),
            durable=True
        )

    def on_consumer_channel_open(self, channel, consumer):
        log.info(f"Consumer channel opened for queue: {consumer.get_queue()}")
        consumer.channel = channel

        # Declare consumer queue
        channel.queue_declare(
            queue=consumer.get_queue(),
            durable=True
        )

        channel.basic_consume(
            queue=consumer.get_queue(),
            on_message_callback=consumer.on_message,
            auto_ack=False
        )

    def on_connection_closed(self, connection, reason):
        log.warning("Connection closed: %s", reason)

    def run(self):
        while True:
            try:
                self.connection = self.connect()
                self.connection.ioloop.start()
            except Exception as e:
                log.error(f"RabbitMQ connection failed: {e}")
                log.info("Retrying in 5 seconds...")
                import time
                time.sleep(5)

    def run_in_background(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def is_ready(self):
        if self.connection is None or not self.connection.is_open:
            return False
        for producer in self.producers:
            if producer.channel is None:
                return False
        return True