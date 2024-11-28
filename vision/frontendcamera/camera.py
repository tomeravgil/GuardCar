import socket
from picamera2 import Picamera2
from PIL import Image
import io
import struct

# Server details
HOST = "0.0.0.0" 
PORT = 5000       

def send_image_to_server(image_array):
    """
    Converts an image array into a grayscale JPEG, resizes it, and sends it to the server.

    Parameters:
    - image_array: numpy array representation of the image captured by the camera.
    """

    # Convert the image array to a PIL Image
    img = Image.fromarray(image_array)
    grayscale_img = img.convert("L")
    
    # Resize the grayscale image (optional: adjust to required size, e.g., 640x480)
    resized_img = grayscale_img.resize((640, 480))  
    
    # Save to a buffer in JPEG format
    buffer = io.BytesIO()
    resized_img.save(buffer, format="JPEG", quality=85)
    image_data = buffer.getvalue()

    # Send image size and data
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        
        # Send the size of the image data first
        size = len(image_data)
        client_socket.sendall(struct.pack(">I", size))  # Send the size as 4-byte unsigned integer
        client_socket.sendall(image_data)  # Send the actual image data
        
        print(f"Sent {size} bytes of grayscale image data")

        # Receive response from the server
        response = client_socket.recv(4096)
        print("Server response:", response.decode('utf-8'))

# Initialize the camera
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()

try:
    while True:
        image = camera.capture_array()
        
        send_image_to_server(image)
        
except KeyboardInterrupt:
    camera.stop()
    print("Camera stopped.")

