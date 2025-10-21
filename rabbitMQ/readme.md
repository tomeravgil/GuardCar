# RabbitMQ Examples (Python)

Simple Python producer/consumer examples using RabbitMQ with `pika`, plus a small utility (`queues.py`) to create durable queues with retry logic.

## Contents
- **`exampleProducer.py`**: Sends a message to the `suspicion` queue
- **`exampleConsumer.py`**: Consumes messages from the `suspicion` queue with manual acks
- **`queues.py`**: Creates durable queues based on environment variables (with connection retries)

## Prerequisites
- **Python 3.8+**
- **pika** Python library
- **RabbitMQ** accessible at the configured host
  - Local install or Docker container

## Installation
```bash
pip install pika
```

## Running RabbitMQ locally (Docker)
If you don’t already have a broker running, start one with management UI:
```bash
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=guest \
  -e RABBITMQ_DEFAULT_PASS=guest \
  rabbitmq:3-management
```
Management UI: http://localhost:15672 (default user/pass: `guest`/`guest`)

## Quick start
1. **Create queues** (optional for local examples; both scripts declare the queue too):
   - Default env in `queues.py` targets a container host named `rabbitmq`. Override to reach localhost:
     ```bash
     # Windows PowerShell example
     setx AMQP_HOST "localhost"
     setx AMQP_USER "guest"
     setx AMQP_PASS "guest"
     setx QUEUES "suspicion"
     ```
     Then open a new terminal and run:
     ```bash
     python queues.py
     ```
2. **Start the consumer** (recommended first):
   ```bash
   python exampleConsumer.py
   ```
   You should see: `Waiting for messages on 'suspicion'. Press CTRL+C to exit.`
3. **Send messages with the producer** (in a second terminal):
   ```bash
   python exampleProducer.py "hello from producer"
   ```
   The consumer should print the message and ack it.

## Script details
- **`exampleConsumer.py`**
  - Connects to `HOST=localhost`, `USER=guest`, `PASS=guest`, `VHOST=/` (edit in file if needed)
  - Declares durable queue `suspicion`
  - Uses `basic_qos(prefetch_count=1)` and manual acks in `on_msg`

- **`exampleProducer.py`**
  - Same connection settings as consumer
  - Declares the same durable queue `suspicion`
  - Publishes persistent messages (`delivery_mode=2`) to default exchange with `routing_key="suspicion"`

- **`queues.py`**
  - Reads connection and queue config from environment variables
  - Retries connection until RabbitMQ is reachable, then declares durable queues

## Configuration (queues.py)
`queues.py` reads the following environment variables:
- `AMQP_HOST` (default: `rabbitmq`)
- `AMQP_PORT` (default: `5672`)
- `AMQP_USER` (default: `app`)
- `AMQP_PASS` (default: `app_pass`)
- `AMQP_VHOST` (default: `/`)
- `QUEUES` (default: `suspicion`) — comma-separated list, e.g. `"suspicion,alerts,events"`

For local Docker with default `guest/guest` and localhost:
```bash
# PowerShell
setx AMQP_HOST "localhost"
setx AMQP_USER "guest"
setx AMQP_PASS "guest"
setx AMQP_VHOST "/"
setx AMQP_PORT "5672"
setx QUEUES "suspicion"
```
Open a new terminal after `setx` to load the values.

## Troubleshooting
- **Connection errors / timeouts**
  - Ensure RabbitMQ is running and reachable at the configured `HOST:PORT`.
  - If using Docker, confirm the container is healthy and ports `5672` and `15672` are published.
  - For `queues.py`, watch the retry logs `[x/y] Waiting for RabbitMQ...`.

- **Auth failures**
  - Verify username/password and vhost match your broker.
  - For default Docker image, `guest/guest` only works from localhost unless changed.

- **Queue not found**
  - Both example scripts declare `suspicion` as durable. If you change names, update both.

## Notes
- These examples use `pika.BlockingConnection` for simplicity.
- Messages are published as persistent but require durable queues to survive broker restarts (already configured).
- Stop the consumer with `CTRL+C`.

