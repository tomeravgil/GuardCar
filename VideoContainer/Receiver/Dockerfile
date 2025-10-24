# dockerfile
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

COPY VideoContainer/Receiver/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY VideoContainer/Receiver/receiver.py ./receiver.py

ENTRYPOINT ["python", "receiver.py"]
CMD ["--pi-host", "raspberrypi.local"]
