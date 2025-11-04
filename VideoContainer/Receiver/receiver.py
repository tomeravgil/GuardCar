# receiver_oop.py
import socket
import ssl
import cv2
import struct
import numpy as np
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)

#   1. Configuration Class
class Config:
    """Loads config from env vars and command-line args."""

    def __init__(self):
        parser = argparse.ArgumentParser()
        # Argparse default is set by env var, but can be overridden by explicit arg
        parser.add_argument(
            "--pi-host",
            default=os.getenv("PI_HOST"),
            help="Raspberry Pi IP or hostname (can also be set by PI_HOST env var)"
        )
        args = parser.parse_args()

        if not args.pi_host:
            print("Error: --pi-host argument or PI_HOST env var must be set.", file=sys.stderr)
            sys.exit(1)

        self.PI_HOST = args.pi_host
        self.PORT = int(os.getenv("SERVER_PORT", 8443))
        self.WINDOW_NAME = "Dual Camera Stream"


#   2. Display Manager
class DisplayManager:
    """Manages the OpenCV window and user input."""

    def __init__(self, window_name):
        self.window_name = window_name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

    def show_frame(self, frame):
        """Displays a frame and checks for quit key."""
        if frame is None:
            print("Received empty frame, skipping display.")
            return True

        cv2.imshow(self.window_name, frame)
        # Return False if 'q' is pressed, else True
        return cv2.waitKey(1) & 0xFF != ord('q')

    def close(self):
        """Destroys all OpenCV windows."""
        print("Closing display.")
        cv2.destroyAllWindows()


#   3. Main Client Class
class StreamClient:
    """Handles connecting, receiving, and decoding the stream."""

    def __init__(self, config, display_manager):
        self.config = config
        self.display = display_manager
        self.context = self._create_tls_context()
        self.sock = None

    def _create_tls_context(self):
        """Creates a client-side SSL context."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # Accepts insecure dev certification
        return context

    def _recv_all(self, n):
        """Helper to receive exactly n bytes from the socket."""
        data = bytearray()
        while len(data) < n:
            packet = self.sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def connect(self):
        """Establishes and wraps the socket connection."""
        try:
            print(f"Connecting to {self.config.PI_HOST}:{self.config.PORT}...")
            raw_sock = socket.create_connection((self.config.PI_HOST, self.config.PORT), timeout=10)
            self.sock = self.context.wrap_socket(raw_sock, server_hostname=self.config.PI_HOST)
            print(f"Connected to {self.config.PI_HOST}:{self.config.PORT}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def run(self):
        """Main loop to receive and display frames."""
        try:
            while True:
                # 1. Receive frame size
                raw_length = self._recv_all(4)
                if not raw_length:
                    print("Connection closed by server.")
                    break
                frame_length = struct.unpack("!I", raw_length)[0]

                # 2. Receive frame data
                frame_data = self._recv_all(frame_length)
                if not frame_data:
                    print("Incomplete frame received.")
                    break

                # 3. Decode frame
                np_data = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

                # 4. Display frame
                if not self.display.show_frame(frame):
                    print("Quit key pressed, exiting.")
                    break

        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            self.close()

    def close(self):
        """Closes the socket connection."""
        if self.sock:
            print("Closing connection.")
            self.sock.close()


#   4. Main execution
def main():
    config = Config()
    display = DisplayManager(config.WINDOW_NAME)
    client = StreamClient(config, display)

    if not client.connect():
        display.close()
        return

    try:
        client.run()
    except KeyboardInterrupt:
        print("\nCaught interrupt, shutting down...")
    finally:
        client.close()
        display.close()
        print("Receiver exited cleanly.")


if __name__ == "__main__":
    main()