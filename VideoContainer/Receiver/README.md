# Receiver

Connects to the sender and displays the video stream.

## Env vars (`VideoContainer/Receiver/.env`)
- `PI_HOST= Raspberry Pi hostname or IP`
- `SERVER_PORT=8443`

## Local run with venv from project root or VideoContainer/Receiver
* cd VideoContainer/Receiver
* python -m venv .venv
* source venv/bin/activate
* python -m pip install -U pip
* pip install -r .\requirements.txt
* python receiver.py --pi-host <sender-host-or-ip> or run python receiver.py (uses .env)