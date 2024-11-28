# import socket
# import io
# from PIL import Image
# from pycoral.adapters.detect import get_objects
# from pycoral.utils.edgetpu import make_interpreter
# from pycoral.utils.dataset import read_label_file
# from collections import defaultdict
# import numpy as np
# from struct import unpack


# class Detection:
#     """
#     Handles object detection using a TensorFlow Lite model on EdgeTPU.
#     """

#     def __init__(self, 
#                  model="ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite",
#                  label="coco_labels.txt", 
#                  debug=False):
        
#         """
#         Initializes the detection model and loads labels.

#         Parameters:
#         - model (str): Path to the TensorFlow Lite model file.
#         - label (str): Path to the labels file.
#         - debug (bool): Enables debug logging if True.
#         """

#         self.debug = debug

#         # Load the model and labels
#         self.interpreter = make_interpreter(model)
#         self.interpreter.allocate_tensors()
#         self.labels = read_label_file(label)

#     def non_max_suppression(self, objects, iou_threshold=0.4):
#         """
#         Applies Non-Maximum Suppression (NMS) to remove overlapping bounding boxes.

#         Parameters:
#         - objects (list): Detected objects as a list of bounding boxes and scores.
#         - iou_threshold (float): Intersection over Union (IoU) threshold for filtering.

#         Returns:
#         - list: Filtered list of detected objects after NMS.
#         """

#         if len(objects) == 0:
#             return []

#         # Extract bounding boxes and scores
#         boxes = np.array([[obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax] for obj in objects])
#         scores = np.array([obj.score for obj in objects])

#         # Compute the area of each bounding box
#         areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])

#         # Sort by confidence score
#         order = scores.argsort()[::-1]

#         keep = []
#         while order.size > 0:
#             i = order[0]
#             keep.append(objects[i])
            
#             # Compute the IoU for the rest of the boxes
#             xx1 = np.maximum(boxes[i, 0], boxes[order[1:], 0])
#             yy1 = np.maximum(boxes[i, 1], boxes[order[1:], 1])
#             xx2 = np.minimum(boxes[i, 2], boxes[order[1:], 2])
#             yy2 = np.minimum(boxes[i, 3], boxes[order[1:], 3])

#             w = np.maximum(0, xx2 - xx1)
#             h = np.maximum(0, yy2 - yy1)

#             intersection = w * h
#             union = areas[i] + areas[order[1:]] - intersection
#             iou = intersection / union

#             # Keep only boxes with IoU <= threshold
#             order = order[1:][iou <= iou_threshold]

#         return keep

#     def detect_from_image(self, img):
#         """
#         Detects objects from an image.

#         Parameters:
#         - img (PIL.Image): The input image to process.

#         Returns:
#         - dict: A dictionary of detected objects and their counts.
#         """

#         # Preprocess the image
#         img = img.convert('RGB')
#         original_width, original_height = img.width, img.height

#         input_details = self.interpreter.get_input_details()
#         height, width = input_details[0]['shape'][1:3]

#         scale_x = original_width / width
#         scale_y = original_height / height
#         resized_img = img.resize((width, height))
#         input_data = np.asarray(resized_img, dtype=np.uint8)

#         input_index = input_details[0]['index']
#         np.copyto(self.interpreter.tensor(input_index)(), input_data)

#         # Run inference
#         self.interpreter.invoke()

#         # Get detected objects
#         objs = get_objects(self.interpreter, 0.5)
#         threshold = 0.5
#         filtered_objs = [obj for obj in objs if obj.score >= threshold]

#         # Apply Non-Maximum Suppression
#         filtered_objs = self.non_max_suppression(filtered_objs, iou_threshold=0.5)

#         # Detect dangers
#         danger_list = ["person", "bicycle", "car", "motorcycle", "truck", "backpack",
#                        "baseball bat", "knife"]
#         detected_danger = defaultdict(int)

#         for obj in filtered_objs:
#             obj_label = self.labels.get(obj.id, obj.id)
#             if obj_label in danger_list:
#                 detected_danger[obj_label] += 1

#         return dict(detected_danger)


# def start_server(host="0.0.0.0", 
#                  port=5000):
#     """
#     Starts a socket server to receive images, perform detection, and respond with results.

#     Parameters:
#     - host (str): Host address to bind the server.
#     - port (int): Port to bind the server.
#     """

#     model_detection = Detection()
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
#         server.bind((host, port))
#         server.listen(1)
#         print(f"Server listening on {host}:{port}")

#         while True:
#             conn, addr = server.accept()
#             print(f"Connected by {addr}")
#             with conn:
#                 try:
#                     # Receive the size of the image data
#                     size_data = conn.recv(4)  # First 4 bytes indicate size
#                     if not size_data:
#                         print("No size data received")
#                         continue
#                     size = unpack(">I", size_data)[0]
#                     print(f"Expecting {size} bytes of image data")

#                     # Receive the actual image data
#                     data = b""
#                     while len(data) < size:
#                         packet = conn.recv(4096)
#                         if not packet:
#                             break
#                         data += packet

#                     if len(data) == size:
#                         print(f"Received {len(data)} bytes of image data")

#                         # Convert bytes to an image
#                         img = Image.open(io.BytesIO(data))
#                         print("Image successfully loaded")

#                         # Placeholder: Process the image (detection)
#                         detected_danger = model_detection.detect_from_image(img)
#                         print(f"Detected dangers: {detected_danger}")

#                         # Send results back to the client
#                         response = str(detected_danger).encode('utf-8')
#                         conn.sendall(response)
#                         print("Results sent back to the client")
#                     else:
#                         print(f"Incomplete data received. Expected {size} bytes, got {len(data)} bytes.")

#                 except Exception as e:
#                     print(f"Error: {e}")


# if __name__ == "__main__":
#     start_server()

import socket
import struct
import io
from PIL import Image
from collections import defaultdict
from pycoral.adapters.detect import get_objects
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.dataset import read_label_file
import numpy as np


class Detection:
    """
    Handles object detection using a TensorFlow Lite model on EdgeTPU.
    """

    def __init__(self, 
                 model="ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite",
                 label="coco_labels.txt", 
                 debug=False):
        self.debug = debug
        self.interpreter = make_interpreter(model)
        self.interpreter.allocate_tensors()
        self.labels = read_label_file(label)

    def non_max_suppression(self, objects, iou_threshold=0.4):
        """
        Applies Non-Maximum Suppression (NMS) to remove overlapping bounding boxes.
        """
        if len(objects) == 0:
            return []
        boxes = np.array([[obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax] for obj in objects])
        scores = np.array([obj.score for obj in objects])
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        order = scores.argsort()[::-1]
        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(objects[i])
            xx1 = np.maximum(boxes[i, 0], boxes[order[1:], 0])
            yy1 = np.maximum(boxes[i, 1], boxes[order[1:], 1])
            xx2 = np.minimum(boxes[i, 2], boxes[order[1:], 2])
            yy2 = np.minimum(boxes[i, 3], boxes[order[1:], 3])
            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)
            intersection = w * h
            union = areas[i] + areas[order[1:]] - intersection
            iou = intersection / union
            order = order[1:][iou <= iou_threshold]
        return keep

    def detect_from_image(self, img):
        """
        Detects objects from an image.
        """
        img = img.convert('RGB')
        original_width, original_height = img.width, img.height
        input_details = self.interpreter.get_input_details()
        height, width = input_details[0]['shape'][1:3]
        scale_x = original_width / width
        scale_y = original_height / height
        resized_img = img.resize((width, height))
        input_data = np.asarray(resized_img, dtype=np.uint8)
        input_index = input_details[0]['index']
        np.copyto(self.interpreter.tensor(input_index)(), input_data)
        self.interpreter.invoke()
        objs = get_objects(self.interpreter, 0.5)
        threshold = 0.5
        filtered_objs = [obj for obj in objs if obj.score >= threshold]
        filtered_objs = self.non_max_suppression(filtered_objs, iou_threshold=0.5)
        danger_list = ["person", "bicycle", "car", "motorcycle", "truck", "backpack", "baseball bat", "knife"]
        detected_danger = defaultdict(int)
        for obj in filtered_objs:
            obj_label = self.labels.get(obj.id, obj.id)
            if obj_label in danger_list:
                detected_danger[obj_label] += 1
        return dict(detected_danger)


def process_image(image_data):
    """
    Converts raw image data into a resized grayscale image.
    """
    try:
        img = Image.open(io.BytesIO(image_data))
        grayscale_img = img.convert("L")  # Convert to grayscale
        resized_img = grayscale_img.resize((640, 480))  # Resize to 640x480
        return resized_img
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def start_server(host="0.0.0.0", port=5000):
    """
    Starts a socket server to receive images, perform detection, and respond with results.
    """
    model_detection = Detection()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen(1)
        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = server.accept()
            print(f"Connected by {addr}")
            with conn:
                try:
                    size_data = conn.recv(4)
                    if not size_data:
                        print("No size data received")
                        continue
                    size = struct.unpack(">I", size_data)[0]
                    print(f"Expecting {size} bytes of image data")
                    data = b""
                    while len(data) < size:
                        packet = conn.recv(4096)
                        if not packet:
                            break
                        data += packet
                    if len(data) == size:
                        print(f"Received {len(data)} bytes of image data")
                        processed_img = process_image(data)
                        if processed_img:
                            detected_danger = model_detection.detect_from_image(processed_img)
                            print(f"Detected dangers: {detected_danger}")
                            response = str(detected_danger).encode('utf-8')
                        else:
                            response = "Failed to process image".encode('utf-8')
                        conn.sendall(response)
                        print("Response sent to the client")
                    else:
                        print(f"Incomplete data received. Expected {size} bytes, got {len(data)} bytes.")
                except Exception as e:
                    print(f"Error: {e}")


if __name__ == "__main__":
    start_server()
