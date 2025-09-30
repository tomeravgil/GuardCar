import cv2
import socket
import ssl
import time
import struct
import numpy as np

# Configuration
CAM0 = 0    #/dev/video0
CAM1 = 1    #/dev/video1
SERVER_HOST = "192.168.1.181"
SERVER_PORT = 8443
CERT_FILE = "cert.pem"
FPS = 30

# OPENCV Video Capture
cap0 = cv2.VideoCapture(CAM0)
cap1 = cv2.VideoCapture(CAM1)

# Set up TLS socket
context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=CERT_FILE)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(sock, server_hostname=SERVER_HOST)
conn.connect((SERVER_HOST, SERVER_PORT))

print("Connected to receiver")

try:
    prev = time.time()
    while True:
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()
        if not ret0 or not ret1:
            print("Failed to capture frames")
            break

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
    cap0.release()
    cap1.release()
    conn.close()
