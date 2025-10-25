# Use a base image for Raspberry Pi (ARM/bookworm)
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system deps for headless OpenCV and camera access
RUN apt-get update && apt-get install -y --no-install-recommends \
    libv4l-dev \
    libjpeg-dev \
    libatlas-base-dev \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy your requirements.txt
COPY requirements.txt .
# Install the headless-opencv version from it
RUN pip install --no-cache-dir -r requirements.txt

# Copy the sender script
COPY sender.py ./

# This EXPOSE is correct
EXPOSE 8443
# This ENTRYPOINT is also correct
ENTRYPOINT ["python", "sender.py"]