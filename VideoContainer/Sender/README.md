# Sender

Streams one or two cameras over TLS.

### Ensure you are running this on a Pi with a connected camera

## Environment variables
Create `VideoContainer/Sender/.env`:
- `HOST=0.0.0.0`
- `SERVER_PORT=8443`
- `FPS=30`
- `JPEG_QUALITY=90`
- `CERT_FILE=/app/cert.pem`
- `KEY_FILE=/app/key.pem`

## Certs
- Create certs: openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -keyout VideoContainer/Sender/key.pem \
  -out VideoContainer/Sender/cert.pem \
  -subj "/CN=$(hostname)"
chmod 600 VideoContainer/Sender/key.pem
- Place `cert.pem` and `key.pem` in `VideoContainer/Sender/` or set `CERT_FILE`/`KEY_FILE`.

## Docker
- Build: `docker build -t guardcar-sender ./VideoContainer/Sender`
- Run: `docker run --rm -it --name sender \
  --network host \
  --privileged \
  -v /run/udev:/run/udev:ro \
  --env-file ./VideoContainer/Sender/.env \
  -v $(pwd)/VideoContainer/Sender/cert.pem:/app/cert.pem:ro \
  -v $(pwd)/VideoContainer/Sender/key.pem:/app/key.pem:ro \
  guardcar-sender`


## Local run (Pi only) with venv from project root or VideoContainer/Sender
- `cd VideoContainer/Sender`
- `python -m venv .venv`
- `source venv/bin/activate`
- `python -m pip install -U pip`
- `pip install -r VideoContainer/Sender/requirements.txt`
- `pip install python3-opencv python3-numpy`
- `sudo apt install python3-picamera2` (Pi only)
- `python VideoContainer/Sender/sender.py`