## INFO

This is a readme on how to run the current rfdetr consumer service. Please keep in mind that it is designed to be run on a vpn to access the rabbitmq server for the processor in the /detection part of this repo. This will work without a vpn on the same network.

## Pre-requisites

Since this section of the repo runs rf-detr on an NVIDIA GPU, you need to have Docker installed with NVIDIA Container Toolkit support. As well, make sure your GPU drivers are updated to the latest drivers.

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

7. To stop the services:

```bash
docker-compose down
```



