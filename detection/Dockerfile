FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*



# IMPORTANT: copy relative paths
COPY detection /app/detection
COPY rabbitMQ /app/rabbitMQ
COPY gRPC /app/gRPC
COPY config /app/config

# Install requirements
RUN pip install --no-cache-dir -r /app/detection/requirements.txt

CMD ["python", "-m", "detection.main"]
