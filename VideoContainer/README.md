# GuardCar — VideoContainer

Lightweight dual-camera streamer for a Raspberry Pi (sender) and a client (receiver). The sender captures two camera streams, stitches them side-by-side, encodes as JPEG frames and streams them over TLS to a connected receiver.

## Features
- Dual-camera capture (Pi)
- Side-by-side combined frames
- Encrypted transport (TLS, port 8443)
- Simple receiver that displays the stream (press `q` to quit)

## Prerequisites
- Python 3.x on both sender (Raspberry Pi) and receiver machines.
- Sender (Pi) packages: opencv-python, numpy, picamera2
- Receiver (Client) packages: opencv-python, numpy
- TLS cert/key files named `cert.pem` and `key.pem` in the sender directory.

## Quick start

Sender (on Raspberry Pi)
1. Place `cert.pem` and `key.pem` next to `sender.py`.
2. Install deps:
   pip install opencv-python numpy picamera2
3. Run:
   python sender.py

Receiver (client)
1. Install deps:
   pip install opencv-python numpy
2. Run (replace with Pi IP/hostname):
   python receiver.py --pi-host <RASPBERRY_PI_IP>

Default TLS port: 8443. Press `q` in the receiver window to exit.

## Generating a self-signed cert (dev)
openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=raspberrypi"

## Troubleshooting
- If the client fails to connect, confirm network reachability and that port 8443 is open.
- If camera init fails on the Pi, verify camera modules and permissions.
- If frames are garbled, check JPEG encoding errors and CPU load.
- For TLS issues in development, ensure cert/key filenames are correct and match those loaded by sender.py.

## Further info
See INSTRUCTIONS.md in this directory for more detailed run and troubleshooting steps.

