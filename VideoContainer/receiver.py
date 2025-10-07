import socket
import ssl
import cv2
import struct
import numpy as np
import argparse

PORT = 8443

def recv_recording(sock, n):
    """Receive n bytes from the socket"""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def main(host_pi):
    context = ssl.create_default_context()
    context.check_hostname= False
    context.verify_mode = ssl.CERT_NONE # Accepts insecure dev certification

    with socket.create_connection((host_pi, PORT)) as raw_sock:
        with context.wrap_socket(raw_sock, server_hostname=host_pi) as sock:
            print(f"Connected to {host_pi}:{PORT}")
            while True:
                raw_length = recv_recording(sock,4)
                if not raw_length:
                    print(f"Connection closed")
                    break
                frame_length = struct.unpack("!I", raw_length)[0]
                frame_data = recv_recording(sock, frame_length)
                if not frame_data:
                    print("Incomplete frame")
                    break
                np_data = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                if frame is None:
                    print("Failed to decode frame")
                    continue
                cv2.imshow("Dual Camera Stream", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'): # Press 'q' to quit
                    break
    cv2.destroyAllWindows()
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pi-host", required=True, help="Raspberry Pi IP or hostname")
    args = parser.parse_args()
    main(args.pi_host)