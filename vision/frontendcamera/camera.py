import cv2
import socket
import threading
import struct
import numpy as np
from picamera2 import Picamera2

# Server details
HOST = "0.0.0.0"  # Update with server's IP if not local
PORT = 5000       # Port used by the server

# Initialize variables for the server response
server_response = "{}"  # Default JSON response

# Lock for thread-safe access to the server response
response_lock = threading.Lock()

def send_frame_to_server(frame):
    """
    Sends a single video frame to the server in the background.

    Parameters:
    - frame: The video frame as a numpy array.
    """
    global server_response
    try:
        # Encode the frame as a JPEG image
        _, frame_encoded = cv2.imencode('.jpg', frame)
        frame_data = frame_encoded.tobytes()
        frame_size = len(frame_data)

        # Open a socket connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))

            # Send frame size and data
            client_socket.sendall(struct.pack(">I", frame_size))
            client_socket.sendall(frame_data)

            # Receive the response from the server
            response = client_socket.recv(4096).decode('utf-8')

            # Update the server response safely
            with response_lock:
                server_response = response

    except Exception as e:
        print(f"Error sending frame to server: {e}")

def capture_and_display():
    """
    Captures video frames, sends them to the server, and displays the video with server responses.
    """
    global server_response

    # Initialize the PiCamera2
    camera = Picamera2()
    camera.configure(camera.create_video_configuration(main={"size": (640, 480)}))
    camera.start()

    try:
        while True:
            # Capture the current frame
            frame = camera.capture_array()

            # Start a thread to send the frame to the server
            threading.Thread(target=send_frame_to_server, args=(frame,), daemon=True).start()

            # Overlay the server response as text on the frame
            with response_lock:
                overlay_text = f"Server Response: {server_response} FPS: {camera.frame_rate}"
            cv2.putText(frame, overlay_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Display the video frame
            cv2.imshow("Video Stream", frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Interrupted by user.")

    finally:
        # Clean up resources
        camera.stop()
        cv2.destroyAllWindows()
        print("Video stream stopped.")

if __name__ == "__main__":
    capture_and_display()

