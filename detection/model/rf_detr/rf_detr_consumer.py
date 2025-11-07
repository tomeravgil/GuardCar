import pika
import json
class RFDETRConsumer:
    def __init__(self, 
                    user, 
                    password,
                    host, 
                    vhost, 
                    rf_detection_service):
        self.user = user
        self.password = password
        self.host = host
        self.vhost = vhost
        self.connection = None
        self.consume_channel = None
        self.produce_channel = None
        self.rf_detection = rf_detection_service
        
    def connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host, port=5672, virtual_host=self.vhost,
            credentials=pika.PlainCredentials(self.user, self.password)
        ))
        self.consume_channel = self.connection.channel()
        self.consume_channel.queue_declare(queue="rf-detr-suspicion-task", durable=True)
        self.produce_channel = self.connection.channel()
        self.produce_channel.queue_declare(queue="rf-detr-suspicion-result", durable=True)

    def on_message(self, channel, method, properties, body):
        # Run inference
        inference_result = self.rf_detection.detect(body)

        # Convert RF-DETR predictions → serializable list
        detections = []
        for pred in inference_result.predictions:
            x1 = pred.x - pred.width / 2
            y1 = pred.y - pred.height / 2
            x2 = pred.x + pred.width / 2
            y2 = pred.y + pred.height / 2

            detections.append({
                "bbox": [x1, y1, x2, y2],
                "class": pred.class_name,
                "confidence": pred.confidence
            })

        # Publish JSON back to reply queue
        self.produce_channel.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=json.dumps(detections).encode("utf-8")
        )

        channel.basic_ack(delivery_tag=method.delivery_tag)
     

    def start(self):
        self.consume_channel.basic_qos(prefetch_count=1)
        self.consume_channel.basic_consume(queue="rf-detr-suspicion-task", on_message_callback=self.on_message, auto_ack=False)
        try:
            self.consume_channel.start_consuming()
        except KeyboardInterrupt:
            self.consume_channel.stop_consuming()
            self.connection.close()
            print("Consumer stopped.")