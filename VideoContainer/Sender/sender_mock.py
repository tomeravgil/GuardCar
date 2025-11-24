# sender_mock.py - Mock version for testing without Pi cameras
import sys
import cv2
import socket
import ssl
import time
import struct
import numpy as np
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import threading
import queue
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)

#   1. Configuration Class
class Config:
    """Loads all configuration from environment variables."""

    def __init__(self):
        # Streaming settings
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.SERVER_PORT = int(os.getenv("SERVER_PORT", 8443))
        self.CERT_FILE = os.getenv("CERT_FILE", "cert.pem")
        self.KEY_FILE = os.getenv("KEY_FILE", "key.pem")
        self.FPS = int(os.getenv("FPS", 30))
        self.JPEG_QUALITY = int(os.getenv("JPEG_QUALITY", 90))
        self.FRAME_INTERVAL = 1.0 / self.FPS
        
        # Recording settings
        self.MINIO_API_URL = os.getenv("MINIO_API_URL", "http://localhost:8000")
        self.CAMERA_ID = os.getenv("CAMERA_ID", "CAM001")
        self.LOCATION = os.getenv("LOCATION", "Test Location")
        self.RECORDING_DIR = Path(os.getenv("RECORDING_DIR", "./recordings"))
        self.RECORDING_DIR.mkdir(exist_ok=True)
        
        # Control API settings
        self.CONTROL_API_PORT = int(os.getenv("CONTROL_API_PORT", 8080))


#   2. Mock Camera Manager
class MockCameraManager:
    """Simulates dual cameras with generated frames."""

    def __init__(self):
        print("🎬 Mock cameras initialized (640x480 each)")
        self.frame_count = 0
        
    def get_combined_frame(self):
        """Generates a synthetic dual-camera frame."""
        self.frame_count += 1
        
        # Create two 640x480 frames with different colors
        # Left camera (blue-tinted)
        left_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        left_frame[:, :] = (100, 50, 0)  # BGR: blue-tinted
        
        # Right camera (green-tinted)
        right_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        right_frame[:, :] = (0, 100, 50)  # BGR: green-tinted
        
        # Add text overlays
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cv2.putText(left_frame, "LEFT CAMERA", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(left_frame, f"Frame: {self.frame_count}", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(left_frame, timestamp, (50, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(right_frame, "RIGHT CAMERA", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(right_frame, f"Frame: {self.frame_count}", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(right_frame, timestamp, (50, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw a moving circle to show motion
        circle_x = int(320 + 200 * np.sin(self.frame_count * 0.1))
        circle_y = int(240 + 100 * np.cos(self.frame_count * 0.1))
        cv2.circle(left_frame, (circle_x, circle_y), 30, (0, 255, 255), -1)
        cv2.circle(right_frame, (circle_x, circle_y), 30, (255, 0, 255), -1)
        
        # Combine horizontally (1280x480)
        combined = np.hstack((left_frame, right_frame))
        
        return combined

    def close(self):
        """Mock cleanup."""
        print("Mock cameras closed.")


#   3. Video Recorder (Same as real version)
class VideoRecorder:
    """Handles video recording and uploading to MinIO."""
    
    def __init__(self, config):
        self.config = config
        self.is_recording = False
        self.video_writer = None
        self.current_filename = None
        self.recording_start_time = None
        self.frame_count = 0
        
        # Upload queue and worker
        self.upload_queue = queue.Queue()
        self.upload_thread = threading.Thread(target=self._upload_worker, daemon=True)
        self.upload_thread.start()
        
        self.lock = threading.Lock()
    
    def start_recording(self):
        """Start recording to a new video file."""
        with self.lock:
            if self.is_recording:
                print("Already recording!")
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.current_filename = self.config.RECORDING_DIR / f"video_{self.config.CAMERA_ID}_{timestamp}.mp4"
            
            # H.264 codec, 1280x480 (dual camera side-by-side)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                str(self.current_filename),
                fourcc,
                self.config.FPS,
                (1280, 480)  # Combined width x height
            )
            
            self.is_recording = True
            self.recording_start_time = datetime.now()
            self.frame_count = 0
            print(f"🔴 Recording started: {self.current_filename}")
            return True
    
    def write_frame(self, frame):
        """Add frame to current recording (thread-safe)."""
        with self.lock:
            if self.is_recording and self.video_writer:
                self.video_writer.write(frame)
                self.frame_count += 1
    
    def stop_recording(self):
        """Stop recording and queue file for upload."""
        with self.lock:
            if not self.is_recording:
                print("Not currently recording!")
                return False
            
            self.is_recording = False
            if self.video_writer:
                self.video_writer.release()
                duration = (datetime.now() - self.recording_start_time).total_seconds()
                print(f"⏹️  Recording stopped: {self.current_filename}")
                print(f"   Duration: {duration:.1f}s, Frames: {self.frame_count}")
                
                # Queue for upload
                self.upload_queue.put(self.current_filename)
                self.current_filename = None
                return True
    
    def get_status(self):
        """Get current recording status."""
        with self.lock:
            if self.is_recording:
                duration = (datetime.now() - self.recording_start_time).total_seconds()
                return {
                    "recording": True,
                    "filename": str(self.current_filename.name) if self.current_filename else None,
                    "duration_seconds": round(duration, 1),
                    "frames": self.frame_count
                }
            return {"recording": False}
    
    def _upload_worker(self):
        """Background thread that uploads completed videos."""
        while True:
            video_path = self.upload_queue.get()
            if video_path is None:  # Poison pill
                break
            
            try:
                self._upload_video(video_path)
            except Exception as e:
                print(f"❌ Upload failed for {video_path}: {e}")
            
            self.upload_queue.task_done()
    
    def _upload_video(self, video_path):
        """Upload video file to MinIO API."""
        print(f"📤 Uploading {video_path.name} to {self.config.MINIO_API_URL}...")
        
        try:
            with open(video_path, 'rb') as f:
                files = {'file': (video_path.name, f, 'video/mp4')}
                data = {
                    'title': f'Recording from {self.config.CAMERA_ID}',
                    'camera_id': self.config.CAMERA_ID,
                    'location': self.config.LOCATION,
                    'description': f'Dual mirror camera recording (TEST)',
                    'timestamp': datetime.now().isoformat()
                }
                
                response = requests.post(
                    f"{self.config.MINIO_API_URL}/api/videos/upload",
                    files=files,
                    data=data,
                    timeout=300
                )
            
            # File is now closed - add small delay for Windows to release handle
            time.sleep(0.5)
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Uploaded successfully as {result['video_id']}")
                
                # Delete local file after successful upload
                try:
                    video_path.unlink()
                    print(f"🗑️  Deleted local file: {video_path.name}")
                except PermissionError:
                    print(f"⚠️  Could not delete {video_path.name} (file in use - will retry)")
                    # Optionally: implement retry logic here
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Upload error: {e}")
        
        
    def close(self):
        """Cleanup resources."""
        if self.is_recording:
            self.stop_recording()
        
        # Stop upload thread
        self.upload_queue.put(None)
        self.upload_thread.join()


#   4. Control API Server (Same as real version)
class ControlAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler for recording control."""
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"[Control API] {format % args}")
    
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/status':
            status = self.server.recorder.get_status()
            self._set_headers(200)
            self.wfile.write(json.dumps(status).encode())
        
        elif self.path == '/health':
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/start':
            success = self.server.recorder.start_recording()
            if success:
                self._set_headers(200)
                self.wfile.write(json.dumps({"message": "Recording started"}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Already recording"}).encode())
        
        elif self.path == '/stop':
            success = self.server.recorder.stop_recording()
            if success:
                self._set_headers(200)
                self.wfile.write(json.dumps({"message": "Recording stopped"}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Not recording"}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())


class ControlAPIServer(HTTPServer):
    """Custom HTTP server that holds reference to recorder."""
    
    def __init__(self, server_address, RequestHandlerClass, recorder):
        super().__init__(server_address, RequestHandlerClass)
        self.recorder = recorder


#   5. Main Stream Server (Same as real version)
class StreamServer:
    """Handles networking, SSL, streaming frames, and recording."""

    def __init__(self, config, camera_manager, recorder):
        self.config = config
        self.camera_manager = camera_manager
        self.recorder = recorder
        self.context = self._create_tls_context()
        self.server_sock = self._create_server_socket()
        self.jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), self.config.JPEG_QUALITY]
        self.running = True

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
        sock.settimeout(1.0)
        try:
            sock.bind((self.config.HOST, self.config.SERVER_PORT))
            sock.listen(1)
            print(f"📹 Stream server listening on {self.config.HOST}:{self.config.SERVER_PORT}")
            return sock
        except Exception as e:
            print(f"FATAL: Could not bind to port: {e}")
            sys.exit(1)

    def run(self):
        """Main server loop to accept clients."""
        while self.running:
            try:
                raw_connection, client_address = self.server_sock.accept()
                print(f"Connection from {client_address}")
                self._handle_client(raw_connection)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Error accepting connection: {e}")

    def _handle_client(self, raw_connection):
        """Manages the entire lifecycle of a single client connection."""
        try:
            with self.context.wrap_socket(raw_connection, server_side=True) as connection:
                prev_time = time.time()
                
                while self.running:
                    # 1. Get Frame
                    frame = self.camera_manager.get_combined_frame()
                    
                    # 2. Record frame if recording is active
                    self.recorder.write_frame(frame)
                    
                    # 3. Encode Frame for streaming
                    encoded, buffer = cv2.imencode('.jpg', frame, self.jpeg_params)
                    if not encoded:
                        print("Failed to encode frame")
                        continue

                    # 4. Send Frame to client
                    data = buffer.tobytes()
                    connection.sendall(struct.pack("!I", len(data)) + data)

                    # 5. Maintain FPS
                    elapsed = time.time() - prev_time
                    delay = max(0.0, self.config.FRAME_INTERVAL - elapsed)
                    time.sleep(delay)
                    prev_time = time.time()

        except (socket.error, ssl.SSLError, struct.error) as e:
            print(f"Client disconnected: {e}")
        except Exception as e:
            print(f"An unexpected error occurred with client: {e}")
        finally:
            raw_connection.close()

    def close(self):
        """Closes the main server socket."""
        print("Closing stream server.")
        self.running = False
        self.server_sock.close()


#  6. Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("🎬 MOCK MODE - Simulating Raspberry Pi Cameras")
    print("=" * 60)
    
    config = Config()
    cam_manager = None
    stream_server = None
    recorder = None
    control_api = None
    control_thread = None
    
    try:
        # Initialize components with MOCK camera
        cam_manager = MockCameraManager()  # <-- ONLY DIFFERENCE
        recorder = VideoRecorder(config)
        stream_server = StreamServer(config, cam_manager, recorder)
        
        # Start Control API in separate thread
        control_api = ControlAPIServer(
            ('0.0.0.0', config.CONTROL_API_PORT),
            ControlAPIHandler,
            recorder
        )
        control_thread = threading.Thread(target=control_api.serve_forever, daemon=True)
        control_thread.start()
        print(f"🎛️  Control API listening on http://0.0.0.0:{config.CONTROL_API_PORT}")
        print(f"   Endpoints:")
        print(f"   - POST /start  - Start recording")
        print(f"   - POST /stop   - Stop recording")
        print(f"   - GET  /status - Get recording status")
        print(f"   - GET  /health - Health check")
        print()
        print("🧪 Testing commands:")
        print(f"   curl -X POST http://localhost:{config.CONTROL_API_PORT}/start")
        print(f"   curl -X POST http://localhost:{config.CONTROL_API_PORT}/stop")
        print(f"   curl http://localhost:{config.CONTROL_API_PORT}/status")
        print("=" * 60)
        
        # Start streaming server (blocking)
        stream_server.run()
        
    except KeyboardInterrupt:
        print("\nCaught interrupt, shutting down...")
    finally:
        if stream_server:
            stream_server.close()
        if recorder:
            recorder.close()
        if control_api:
            control_api.shutdown()
        if cam_manager:
            cam_manager.close()
        print("Mock sender exited cleanly.")