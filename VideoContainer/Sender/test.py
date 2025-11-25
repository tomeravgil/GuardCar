import socket
import struct
import cv2
import numpy as np

def receive_all(sock, length):
    """Helper to receive exactly `length` bytes."""
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

def main():
    ip = input("Enter Raspberry Pi IP: ")
    port = int(input("Enter port (default 8443): ") or 8443)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"Connecting to {ip}:{port} ...")

    try:
        s.connect((ip, port))
        print("Connected! Streaming frames...")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    try:
        while True:
            # --- Receive 4-byte frame length ---
            header = receive_all(s, 4)
            if not header:
                print("Disconnected from server.")
                break

            frame_len = struct.unpack("!I", header)[0]

            # --- Receive frame bytes ---
            jpg_bytes = receive_all(s, frame_len)
            if jpg_bytes is None:
                print("Stream ended.")
                break

            # --- Decode JPEG to OpenCV image ---
            img_array = np.frombuffer(jpg_bytes, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if frame is None:
                print("Decode failed.")
                continue

            # --- Display frame ---
            cv2.imshow("GuardCar Stream", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Quitting stream.")
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    finally:
        s.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
