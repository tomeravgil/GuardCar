# Sender

Streams one or two cameras over TLS.

## Env vars (`VideoContainer/Sender/.env`)
- `HOST=0.0.0.0`
- `SERVER_PORT=8443`
- `FPS=30`
- `JPEG_QUALITY=90`
- `CERT_FILE=/app/cert.pem`
- `KEY_FILE=/app/key.pem`

## Local run (Pi or webcam fallback on Windows)
- `pip install -r VideoContainer/Sender/requirements.txt`
- `python VideoContainer/Sender/sender.py`

## Docker
- Build: `docker build -t guardcar-sender ./VideoContainer/Sender`
- Run: `docker run --rm -it --name sender \
  --network host \
  --privileged \
  -v /run/udev:/run/udev:ro \
  --env-file ./VideoContainer/Sender/.env \
  -v /path/to/cert.pem:/app/cert.pem:ro \
  -v /path/to/key.pem:/app/key.pem:ro \
  guardcar-sender`

## Certs
- Create certs: openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -keyout VideoContainer/Sender/key.pem \
  -out VideoContainer/Sender/cert.pem \
  -subj "/CN=$(hostname)"
chmod 600 VideoContainer/Sender/key.pem
- Place `cert.pem` and `key.pem` in `VideoContainer/Sender/` or set `CERT_FILE`/`KEY_FILE`.
