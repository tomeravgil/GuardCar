# dockerfile
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/usr/lib/python3/dist-packages

WORKDIR /app

# Add Raspberry Pi repo (for python3-picamera2) and install runtime deps
RUN apt-get update -o Acquire::Retries=3 && apt-get install -y --no-install-recommends \
      curl gnupg ca-certificates \
 && curl -fsSL https://archive.raspberrypi.org/debian/raspberrypi.gpg.key \
    | gpg --dearmor -o /usr/share/keyrings/raspberrypi-archive-keyring.gpg \
 && echo "deb [signed-by=/usr/share/keyrings/raspberrypi-archive-keyring.gpg] http://archive.raspberrypi.org/debian/ bookworm main" \
    > /etc/apt/sources.list.d/raspi.list \
 && apt-get update -o Acquire::Retries=3 && apt-get install -y --no-install-recommends \
      libv4l-0 libjpeg62-turbo libatlas-base-dev ffmpeg python3-picamera2 \
 && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# App
COPY sender.py ./

EXPOSE 8443
ENTRYPOINT ["python", "sender.py"]
