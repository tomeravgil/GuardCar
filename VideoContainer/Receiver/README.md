# Receiver

Connects to the sender and displays the video stream.

## Env vars (`VideoContainer/Receiver/.env`)
- `PI_HOST=raspberrypi.local`
- `SERVER_PORT=8443`

## Local run
- `pip install -r VideoContainer/Receiver/requirements.txt`
- `python VideoContainer/Receiver/receiver.py --pi-host <host>`

## Docker
- Build: `docker build -f VideoContainer/Receiver/Dockerfile -t receiver:latest .`
- Run: `docker run --rm --env-file VideoContainer/Receiver/.env receiver:latest`
