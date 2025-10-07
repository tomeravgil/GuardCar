import pika, sys


# information to be able to connect to the container 
USER = "guest"       
PASS = "guest"       
HOST = "localhost"  
VHOST = "/"

# setting up the AMPQ connection with the correct information 
conn = pika.BlockingConnection(pika.ConnectionParameters(
    host=HOST, port=5672, virtual_host=VHOST,
    credentials=pika.PlainCredentials(USER, PASS)
))
ch = conn.channel()

# Ensure the queue exists 
ch.queue_declare(queue="suspicion", durable=True)

print("Waiting for messages on 'suspicion'. Press CTRL+C to exit.")

# Manual-ack setup so you see it clearly
def on_msg(ch, method, props, body):
    print(f" [x] Got: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Fair dispatch (optional, good habit)
ch.basic_qos(prefetch_count=1)

ch.basic_consume(queue="suspicion", on_message_callback=on_msg, auto_ack=False)
try:
    ch.start_consuming()
except KeyboardInterrupt:
    ch.stop_consuming()
    conn.close()
    print("Consumer stopped.")
