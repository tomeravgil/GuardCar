# GuardCar Video Container

## Layout
- `VideoContainer/Sender/` – streams video over TLS.
- `VideoContainer/Receiver/` – connects and displays the stream.

## Prereqs
- Docker or Python 3.11+.
- `.env` files per app (see each folder).
- Certificates in `VideoContainer/Sender/` or set `CERT_FILE`/`KEY_FILE`.

## Build (from repo root)
- `docker build -f VideoContainer/Sender/Dockerfile -t sender:latest .`
- `docker build -f VideoContainer/Receiver/Dockerfile -t receiver:latest .`

## Run with Docker
- Sender: `docker run --rm --env-file VideoContainer/Sender/.env -p 8443:8443 sender:latest`
- Receiver: `docker run --rm --env-file VideoContainer/Receiver/.env receiver:latest`

## Local dev
- Sender: `pip install -r VideoContainer/Sender/requirements.txt && python VideoContainer/Sender/sender.py`
- Receiver: `pip install -r VideoContainer/Receiver/requirements.txt && python VideoContainer/Receiver/receiver.py --pi-host <host>`

## Notes
- Env precedence: CLI > real env > `.env` > defaults.
- Add `.env` to `.gitignore`.
