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
    Converts raw JPEG image data into a PIL Image.
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
                        continue
                    size = struct.unpack(">I", size_data)[0]
                    data = b""
                    while len(data) < size:
                        packet = conn.recv(4096)
                        if not packet:
                            break
                        data += packet
                    if len(data) == size:
                        img = process_image(data)
                        if img:
                            objs = model_detection.detect_from_image(img)
                            response = str(objs).encode('utf-8')
                        else:
                            response = b"Failed to process image"
                        conn.sendall(response)
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    start_server()
