import cv2
import socket
import ssl
import struct
import numpy as np

# Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8443
CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"

# Set up TLS server
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((SERVER_HOST, SERVER_PORT))
sock.listen(1)

print(f"Listening on {SERVER_HOST}:{SERVER_PORT}")

conn, addr = sock.accept()
tls_connection = context.wrap_socket(conn, server_side = True)
print(f"Connection from {addr}")

try:
    while True:
        # Read frame size
        length_buf = tls_connection.recv(4)
        if not length_buf:
            break
        length, = struct.unpack("!I", length_buf)[0]

        # Read frame data
        data = b""
        while len(data) < length:
            packet = tls_connection.recv(length - len(data))
            if not packet:
                break
            data += packet

        # Decode frame
        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

        # Show merged frame
        cv2.imshow("Merged Cameras", frame)
        if cv2.waitKey(1) == ord("q"):
            break
except KeyboardInterrupt:
    print("Exiting receiver...")

finally:
    tls_connection.close()
    sock.close()
    cv2.destroyAllWindows()