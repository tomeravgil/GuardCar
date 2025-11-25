FROM python:3.11-slim

WORKDIR /app

COPY /detection ./
COPY /rabbitMQ ./
COPY /gRPC ./

RUN pip install --no-cache-dir -r detection/requirements.txt

COPY . .

CMD ["python", "-m", "detection.main"]
