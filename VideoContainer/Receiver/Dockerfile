# dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 libgtk2.0-0 libjpeg-dev ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY VideoContainer/Receiver/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY VideoContainer/Receiver/receiver.py ./receiver.py

ENTRYPOINT ["python", "receiver.py"]
CMD ["--pi-host", "raspberrypi.local"]
