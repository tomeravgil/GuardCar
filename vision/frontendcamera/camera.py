# import socket
# from picamera2 import Picamera2
# from PIL import Image
# import io
# import struct

# # Server details
# HOST = "0.0.0.0" 
# PORT = 5000       

# def send_image_to_server(image_array):
#     """
#     Converts an image array into a grayscale JPEG, resizes it, and sends it to the server.

#     Parameters:
#     - image_array: numpy array representation of the image captured by the camera.
#     """

#     # Convert the image array to a PIL Image
#     img = Image.fromarray(image_array)
#     grayscale_img = img.convert("L")
    
#     # Resize the grayscale image (optional: adjust to required size, e.g., 640x480)
#     resized_img = grayscale_img.resize((640, 480))  
    
#     # Save to a buffer in JPEG format
#     buffer = io.BytesIO()
#     resized_img.save(buffer, format="JPEG", quality=85)
#     image_data = buffer.getvalue()

#     # Send image size and data
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
#         client_socket.connect((HOST, PORT))
        
#         # Send the size of the image data first
#         size = len(image_data)
#         client_socket.sendall(struct.pack(">I", size))  # Send the size as 4-byte unsigned integer
#         client_socket.sendall(image_data)  # Send the actual image data
        
#         print(f"Sent {size} bytes of grayscale image data")

#         # Receive response from the server
#         response = client_socket.recv(4096)
#         print("Server response:", response.decode('utf-8'))

# # Initialize the camera
# camera = Picamera2()
# camera.configure(camera.create_still_configuration())
# camera.start()

# try:
#     while True:
#         image = camera.capture_array()
        
#         send_image_to_server(image)
        
# except KeyboardInterrupt:
#     camera.stop()
#     print("Camera stopped.")

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
        # Convert the frame to bytes
        frame_data = frame.tobytes()
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
    camera.configure(camera.create_still_configuration())
    camera.start()

    try:
        while True:
            # Capture the current frame
            frame = camera.capture_array()

            # Start a thread to send the frame to the server
            threading.Thread(target=send_frame_to_server, args=(frame,), daemon=True).start()

            # Convert the frame to BGR format for OpenCV (if needed)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Overlay the server response as text on the frame
            with response_lock:
                overlay_text = f"Server Response: {server_response}"
            cv2.putText(frame_bgr, overlay_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Display the video frame
            cv2.imshow("Video Stream", frame_bgr)

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
