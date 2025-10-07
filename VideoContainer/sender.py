import cv2
from picamera2 import Picamera2
import socket
import ssl
import time
import struct
import numpy as np

# Configuration
HOST = "0.0.0.0"
SERVER_PORT = 8443
CERT_FILE = "cert.pem"
KEY_FIlE = "key.pem"
FPS = 30

def create_tls_context():
    """Create a TLS context with secure settings"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    try:
        context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FIlE)
        print("Loaded TLS cert/key")
    except Exception as e:
        print("Failed to load cert/key:", e)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    return context
    return context

def main():
    # Initialize cameras
    cam0 = Picamera2(0)
    cam1 = Picamera2(1)

    cam0.start()
    cam1.start()

    context = create_tls_context()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, SERVER_PORT))
        server_sock.listen(1)
        print(f"Server listening on {HOST}:{SERVER_PORT}")

        while True:
            raw_connection, client_address = server_sock.accept()
            print(f"Connection from {client_address}")
            try:
                with context.wrap_socket(raw_connection, server_side=True) as connection:
                    prev = time.time()
                    while True:
                        # Capture frames
                        frame0 = cam0.capture_array()
                        frame1 = cam1.capture_array()

                        # Combine frames side by side
                        combined_frame = np.hstack((frame0, frame1))

                        # Encode frame as JPEG
                        encoded, buffer = cv2.imencode('.jpg', combined_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                        if not encoded:
                            print("Failed to encode frame")
                            continue

                        # Send frame size and data
                        data = buffer.tobytes()
                        size = len(data)
                        connection.sendall(struct.pack("!I", size) + data)

                        # Maintain target FPS
                        elapsed = time.time() - prev
                        delay = max(0.0, (1.0 / FPS) - elapsed)
                        time.sleep(delay)
                        prev = time.time()
            except Exception as e:
                print(f"Client disconnected/error: {e}")
                continue

        # Cleanup (normally unreachable unless loop broken)
        cam0.stop()
        cam1.stop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting sender")