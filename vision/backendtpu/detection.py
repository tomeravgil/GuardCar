import socket
import io
from PIL import Image
from pycoral.adapters.detect import get_objects
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.dataset import read_label_file
from collections import defaultdict
import numpy as np


class Detection:
    def __init__(self, model="ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite",
                 label="coco_labels.txt", debug=False):
        self.debug = debug

        # Load the model and labels
        self.interpreter = make_interpreter(model)
        self.interpreter.allocate_tensors()
        self.labels = read_label_file(label)

    def non_max_suppression(self, objects, iou_threshold=0.4):
        if len(objects) == 0:
            return []

        # Extract bounding boxes and scores
        boxes = np.array([[obj.bbox.xmin, obj.bbox.ymin, obj.bbox.xmax, obj.bbox.ymax] for obj in objects])
        scores = np.array([obj.score for obj in objects])

        # Compute the area of each bounding box
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])

        # Sort by confidence score
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(objects[i])
            
            # Compute the IoU for the rest of the boxes
            xx1 = np.maximum(boxes[i, 0], boxes[order[1:], 0])
            yy1 = np.maximum(boxes[i, 1], boxes[order[1:], 1])
            xx2 = np.minimum(boxes[i, 2], boxes[order[1:], 2])
            yy2 = np.minimum(boxes[i, 3], boxes[order[1:], 3])

            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)

            intersection = w * h
            union = areas[i] + areas[order[1:]] - intersection
            iou = intersection / union

            # Keep only boxes with IoU <= threshold
            order = order[1:][iou <= iou_threshold]

        return keep

    def detect_from_image(self, img):
        # Preprocess the image
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

        # Run inference
        self.interpreter.invoke()

        # Get detected objects
        objs = get_objects(self.interpreter, 0.5)
        threshold = 0.5
        filtered_objs = [obj for obj in objs if obj.score >= threshold]

        # Apply Non-Maximum Suppression
        filtered_objs = self.non_max_suppression(filtered_objs, iou_threshold=0.5)

        # Detect dangers
        danger_list = ["person", "bicycle", "car", "motorcycle", "truck", "backpack",
                       "baseball bat", "knife"]
        detected_danger = defaultdict(int)

        for obj in filtered_objs:
            obj_label = self.labels.get(obj.id, obj.id)
            if obj_label in danger_list:
                detected_danger[obj_label] += 1

        return dict(detected_danger)


def start_server(host="0.0.0.0", port=5000):
    detection_model = Detection(debug=False)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen(1)
        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = server.accept()
            print(f"Connected by {addr}")
            with conn:
                # Receive the image data
                data = b""
                while True:
                    packet = conn.recv(4096)
                    if not packet:
                        break
                    data += packet

                try:
                    # Convert bytes to an image
                    img = Image.open(io.BytesIO(data))

                    # Perform detection
                    detected_danger = detection_model.detect_from_image(img)

                    # Send results back to the client
                    response = str(detected_danger).encode('utf-8')
                    conn.sendall(response)
                except Exception as e:
                    print(f"Error processing image: {e}")


if __name__ == "__main__":
    start_server()
