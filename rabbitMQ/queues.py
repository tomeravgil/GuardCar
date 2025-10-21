import os
import time
import pika

# Reading in the docker compose yaml information 
HOST = os.getenv("AMQP_HOST", "rabbitmq")
PORT = int(os.getenv("AMQP_PORT", "5672"))
USER = os.getenv("AMQP_USER", "app")
PASS = os.getenv("AMQP_PASS", "app_pass")
VHOST = os.getenv("AMQP_VHOST", "/")
QUEUES = [q.strip() for q in os.getenv("QUEUES", "suspicion").split(",") if q.strip()] # list of queues to create 

def connect(max_tries=30, delay_sec=2): 
    # creating the AMQP authentification 
    creds = pika.PlainCredentials(USER, PASS)

    # building the username and password crediential object 
    params = pika.ConnectionParameters(
        host=HOST, port=PORT, virtual_host=VHOST,
        credentials=creds, heartbeat=60, blocked_connection_timeout=30
    )

    # attempts to create queues with a max number of time 
    for attempt in range(1, max_tries + 1):
        # atttempt to create the AMQP queue for communication 
        # between client and server (producer and consumer)
        try:
            return pika.BlockingConnection(params)
        # prints whenever a failure is reached, keeps retrying until success is hit, if not throw error 
        except Exception as e:
            print(f"[{attempt}/{max_tries}] Waiting for RabbitMQ... {e}")
            time.sleep(delay_sec)
    raise SystemExit("RabbitMQ not reachable after retries.")

if __name__ == "__main__":
    # creates a TCP channel to create all the queues
    conn = connect()
    ch = conn.channel()
    for q in QUEUES:
        ch.queue_declare(queue=q, durable=True)  
        print(f"Created durable queue: {q}")
    conn.close()
    print("Done.")