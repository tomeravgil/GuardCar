import pika, sys

USER = "guest"       # same creds as consumer
PASS = "guest"
HOST = "localhost"
VHOST = "/"

conn = pika.BlockingConnection(pika.ConnectionParameters(
    host=HOST, port=5672, virtual_host=VHOST,
    credentials=pika.PlainCredentials(USER, PASS)
))
ch = conn.channel()

# Ensure same queue exists
ch.queue_declare(queue="suspicion", durable=True)

msg = "hello from producer"
if len(sys.argv) > 1:
    msg = " ".join(sys.argv[1:])

# Publish persistent message to the default exchange → routes by routing_key to the queue
ch.basic_publish(
    exchange="",
    routing_key="suspicion",
    body=msg.encode(),
    properties=pika.BasicProperties(delivery_mode=2)  # persistent
)
print(f"Sent: {msg}")
conn.close()
