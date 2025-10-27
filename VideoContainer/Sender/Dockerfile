# dockerfile
# ARM64 base with Raspberry Pi OS userspace and repo preconfigured
FROM ghcr.io/raspberrypi/python:3.11-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# System packages (no extra repo setup needed)
RUN apt-get update -o Acquire::Retries=3 && apt-get install -y --no-install-recommends \
      libv4l-0 libjpeg62-turbo libatlas-base-dev ffmpeg \
      python3-picamera2 python3-opencv python3-numpy \
 && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# App
COPY sender.py ./

EXPOSE 8443
CMD ["python", "/app/sender.py"]
