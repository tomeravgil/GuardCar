# GuardCar VideoContainer Instructions

## Prerequisites

- Python 3.x installed on both sender (Raspberry Pi) and receiver machines.
- Required Python packages:
  - Sender (Pi): `opencv-python`, `numpy`, `picamera2`
  - Receiver (Client): `opencv-python`, `numpy`
- SSL certificate and key files `cert.pem` and `key.pem` placed in the same directory as `sender.py` (exact names are required).
- Network connectivity between sender and receiver (port `8443`).

## Generating a self-signed cert (development)

```bash
openssl req -x509 -newkey rsa:4096 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=raspberrypi"
```

## Running the Sender (Raspberry Pi)

1. Ensure both cameras are connected and detected by the Pi.
2. Place `cert.pem` and `key.pem` in the `VideoContainer` directory.
3. Install dependencies:
   ```bash
   pip install opencv-python numpy picamera2
   ```
4. Run the sender script:
   ```bash
   python sender.py
   ```
   The sender will start streaming video over a secure connection.

## Running the Receiver (Client)

1. Install dependencies:
   ```bash
   pip install opencv-python numpy
   ```
2. Run the receiver script, specifying the Pi's IP address:
   ```bash
   python receiver.py --pi-host <RASPBERRY_PI_IP>
   ```
   Replace `<RASPBERRY_PI_IP>` with the actual IP address or hostname of the Raspberry Pi.

3. The video stream will appear in a window. Press `q` to quit.

## Troubleshooting

- Ensure firewall rules allow traffic on port 8443.
- If SSL certificate errors occur, verify the certificate and key files.
- For camera issues, check hardware connections and permissions.


