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
- Build: `docker build -f VideoContainer/Sender/Dockerfile -t sender:latest .`
- Run: `docker run --rm --env-file VideoContainer/Sender/.env -p 8443:8443 sender:latest`

## Certs
- Place `cert.pem` and `key.pem` in `VideoContainer/Sender/` or set `CERT_FILE`/`KEY_FILE`.
