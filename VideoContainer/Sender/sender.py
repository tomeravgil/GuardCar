# sender_oop.py
import sys
import cv2
from picamera2 import Picamera2
import socket
import ssl
import time
import struct
import numpy as np
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)

#   1. Configuration Class
class Config:
    """Loads all configuration from environment variables."""

    def __init__(self):
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.SERVER_PORT = int(os.getenv("SERVER_PORT", 8443))
        self.CERT_FILE = os.getenv("CERT_FILE", "cert.pem")
        self.KEY_FILE = os.getenv("KEY_FILE", "key.pem")
        self.FPS = int(os.getenv("FPS", 30))
        self.JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", 90))
        self.FRAME_INTERVAL = 1.0 / self.FPS


#   2. Camera Hardware Manager
class CameraManager:
    """Manages the initialization and capturing from Picamera2."""

    def __init__(self):
        try:
            self.cam0 = Picamera2(0)
            self.cam1 = Picamera2(1)
            self.cam0.start()
            self.cam1.start()
            print("Cameras initialized and started.")
        except Exception as e:
            print(f"FATAL: Camera initialization failed: {e}")
            sys.exit(1)

    def get_combined_frame(self):
        """Captures from both cameras and combines them horizontally."""
        frame0 = self.cam0.capture_array()
        frame1 = self.cam1.capture_array()
        return np.hstack((frame0, frame1))

    def close(self):
        """Stops and closes camera resources."""
        print("Stopping cameras...")
        self.cam0.stop()
        self.cam1.stop()


#   3. Main Server Class (The "Use Case")
class StreamServer:
    """Handles networking, SSL, and streaming frames to clients."""

    def __init__(self, config, camera_manager):
        self.config = config
        self.camera_manager = camera_manager
        self.context = self._create_tls_context()
        self.server_sock = self._create_server_socket()
        self.jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), self.config.JPEG_QUALITY]

    def _create_tls_context(self):
        """Create a TLS context with secure settings."""
        print("Creating TLS context...")
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            context.load_cert_chain(certfile=self.config.CERT_FILE, keyfile=self.config.KEY_FILE)
            print("Loaded TLS cert/key")
            return context
        except Exception as e:
            print(f"FATAL: Failed to load cert/key: {e}")
            sys.exit(1)

    def _create_server_socket(self):
        """Binds and listens on the server socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.config.HOST, self.config.SERVER_PORT))
            sock.listen(1)
            print(f"Server listening on {self.config.HOST}:{self.config.SERVER_PORT}")
            return sock
        except Exception as e:
            print(f"FATAL: Could not bind to port: {e}")
            sys.exit(1)

    def run(self):
        """Main server loop to accept clients."""
        while True:
            try:
                raw_connection, client_address = self.server_sock.accept()
                print(f"Connection from {client_address}")
                # We handle clients one by one in this simple design
                self._handle_client(raw_connection)
            except Exception as e:
                print(f"Error accepting connection: {e}")

    def _handle_client(self, raw_connection):
        """Manages the entire lifecycle of a single client connection."""
        try:
            with self.context.wrap_socket(raw_connection, server_side=True) as connection:
                prev_time = time.time()
                while True:
                    # 1. Get Frame
                    frame = self.camera_manager.get_combined_frame()

                    # 2. Encode Frame
                    encoded, buffer = cv2.imencode('.jpg', frame, self.jpeg_params)
                    if not encoded:
                        print("Failed to encode frame")
                        continue

                    # 3. Send Frame
                    data = buffer.tobytes()
                    connection.sendall(struct.pack("!I", len(data)) + data)

                    # 4. Maintain FPS
                    elapsed = time.time() - prev_time
                    delay = max(0.0, self.config.FRAME_INTERVAL - elapsed)
                    time.sleep(delay)
                    prev_time = time.time()

        except (socket.error, ssl.SSLError, struct.error) as e:
            print(f"Client {raw_connection.getpeername()} disconnected: {e}")
        except Exception as e:
            print(f"An unexpected error occurred with client: {e}")
        finally:
            print(f"Cleaning up connection from {raw_connection.getpeername()}")
            raw_connection.close()

    def close(self):
        """Closes the main server socket."""
        print("Closing server socket.")
        self.server_sock.close()


#  4. Main execution
if __name__ == "__main__":
    config = Config()
    cam_manager = None
    stream_server = None
    try:
        cam_manager = CameraManager()
        stream_server = StreamServer(config, cam_manager)
        stream_server.run()
    except KeyboardInterrupt:
        print("\nCaught interrupt, shutting down...")
    finally:
        if stream_server:
            stream_server.close()
        if cam_manager:
            cam_manager.close()
        print("Sender exited cleanly.")