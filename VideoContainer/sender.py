import cv2
from picamera2 import Picamera2
import socket
import ssl
import time
import struct
import numpy as np

# Configuration
SERVER_HOST = "192.168.1.181"
SERVER_PORT = 8443
CERT_FILE = "cert.pem"
FPS = 30

# Initialize cameras
cam0 = Picamera2()
cam1 = Picamera2()

cam0.start()
cam1.start()

# Set up TLS socket
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=CERT_FILE)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(sock, server_hostname=SERVER_HOST)
conn.connect((SERVER_HOST, SERVER_PORT))



print("Connected to receiver")

try:
    prev = time.time()
    while True:
        frame0 = cam0.capture_array()
        frame1 = cam1.capture_array()

        # Resize frames to the same height(in case of different camera resolutions)
        height = min(frame0.shape[0], frame1.shape[0])
        frame0 = cv2.resize(frame0, (int(frame0.shape[1] * height / frame0.shape[0]), height))
        frame1 = cv2.resize(frame1, (int(frame1.shape[1] * height / frame1.shape[0]), height))

        # Combine frames side by side
        merged_frame = np.hstack((frame0, frame1))

        # Encode frame as JPEG
        encoded, buffer = cv2.imencode('.jpg',  merged_frame)
        if not encoded:
            print("Failed to encode frame")
            continue

        # Send frame size and data
        data = buffer.tobytes()

        # Send length and data
        conn.sendall(struct.pack("!I", len(data)) + data)
        # Maintain target FPS
        time.sleep(max(0.0, (1.0 / FPS) - (time.time() - prev)))
        prev = time.time()
except KeyboardInterrupt:
    print("Exiting sender")
finally:
    cam0.stop()
    cam1.stop()
    conn.close()