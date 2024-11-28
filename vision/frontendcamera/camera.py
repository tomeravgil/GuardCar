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

import socket
from picamera2 import Picamera2
from PIL import Image
import io
import struct

# Server details
HOST = "0.0.0.0"  # Server IP
PORT = 5000       # Server port

def send_image_to_server(image_array):
    """
    Sends an image to the server and receives the processed image.

    Parameters:
    - image_array: numpy array representation of the image captured by the camera.
    """

    # Convert the image array to a PIL Image
    img = Image.fromarray(image_array)

    # Save the image to a buffer in JPEG format
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    image_data = buffer.getvalue()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Connect to the server
        client_socket.connect((HOST, PORT))

        # Send the size of the image data
        size = len(image_data)
        client_socket.sendall(struct.pack(">I", size))  # Send as 4-byte unsigned integer
        client_socket.sendall(image_data)  # Send the actual image data

        print(f"Sent {size} bytes of image data")

        # Receive the size of the processed image
        processed_size_data = client_socket.recv(4)
        if not processed_size_data:
            print("No size data received from server")
            return
        processed_size = struct.unpack(">I", processed_size_data)[0]

        # Receive the processed image data
        processed_data = b""
        while len(processed_data) < processed_size:
            packet = client_socket.recv(4096)
            if not packet:
                break
            processed_data += packet

        if len(processed_data) == processed_size:
            # Convert the received bytes back to an image
            processed_img = Image.open(io.BytesIO(processed_data))
            processed_img.show()  # Display the processed image
            print("Processed image received and displayed")
        else:
            print(f"Incomplete processed data received. Expected {processed_size} bytes, got {len(processed_data)} bytes.")


# Initialize the camera
camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()

try:
    while True:
        # Capture an image from the camera
        image = camera.capture_array()

        # Send the image to the server and receive the processed image
        send_image_to_server(image)
        
except KeyboardInterrupt:
    # Stop the camera on exit
    camera.stop()
    print("Camera stopped.")
