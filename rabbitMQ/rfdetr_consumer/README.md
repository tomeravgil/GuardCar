## How to start up the consumer

1. Be in the rabbitMQ/rfdetr_consumer directory

2. Set up RabbitMQ User Defaults:

ex. in terminal 

```bash
RABBITMQ_DEFAULT_USER=guardcar \
RABBITMQ_DEFAULT_PASS=supersecretpassword \
RABBITMQ_DEFAULT_VHOST=gc \
```

3. Build the Docker image:
   
```bash
docker-compose build
```

4. Start the services:

```bash
docker-compose up -d
```

5. Check that the services are running:

```bash
docker-compose ps
```

6. View logs to verify the consumer is working:

```bash
docker-compose logs -f rfdetr-consumer
```

