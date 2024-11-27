from pycoral.adapters.detect import get_objects
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.dataset import read_label_file
from PIL import Image, ImageDraw
from collections import defaultdict
import numpy as np

def non_max_suppression(objects, iou_threshold=0.4):
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
        order = order[1:]

        # Compute IoU (Intersection over Union)
        overlaps = []
        for j in order:
            xx1 = max(boxes[i, 0], boxes[j, 0])
            yy1 = max(boxes[i, 1], boxes[j, 1])
            xx2 = min(boxes[i, 2], boxes[j, 2])
            yy2 = min(boxes[i, 3], boxes[j, 3])

            w = max(0, xx2 - xx1)
            h = max(0, yy2 - yy1)

            intersection = w * h
            union = areas[i] + areas[j] - intersection
            overlaps.append(intersection / union)

        # Suppress boxes with IoU above the threshold
        overlaps = np.array(overlaps)
        order = order[overlaps <= iou_threshold]

    return keep


def detect(model="ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite",
           label="coco_labels.txt",
           image="",
           debug=True,
           output=""):

    if not image:
        print("No image provided.")
        return
    
    # Load the model and labels
    interpreter = make_interpreter(model)
    interpreter.allocate_tensors()
    labels = read_label_file(label)

    # Load the image
    img = Image.open(image).convert('RGB')
    original_width, original_height = img.width, img.height

    # Get input details
    input_details = interpreter.get_input_details()
    height, width = input_details[0]['shape'][1:3]

    # Preprocess the image
    resized_img = img.resize((width, height))
    input_data = np.asarray(resized_img, dtype=np.uint8)

    # Copy data to the tensor
    input_index = input_details[0]['index']
    np.copyto(interpreter.tensor(input_index)(), input_data)

    # Run inference
    interpreter.invoke()

    # Get detected objects
    objs = get_objects(interpreter, 0.5)
    threshold = 0.5
    filtered_objs = [obj for obj in objs if obj.score >= threshold]

    # Apply Non-Maximum Suppression
    filtered_objs = non_max_suppression(filtered_objs, iou_threshold=0.5)

    danger_list = ["person", "bicycle", "car", "motorcycle", "truck", "backpack", 
                   "baseball bat", "knife"]
    detected_danger = defaultdict(int)

    if not debug:
        for obj in filtered_objs:
            obj_label = labels.get(obj.id, obj.id)
            if obj_label in danger_list:
                detected_danger[obj_label] += 1
        return dict(detected_danger)

    # Draw bounding boxes in debug mode
    draw = ImageDraw.Draw(img)
    scale_x = original_width / width
    scale_y = original_height / height

    for obj in filtered_objs:
        obj_label = labels.get(obj.id, obj.id)
        if obj_label in danger_list:
            detected_danger[obj_label] += 1

            # Scale bounding box to original image dimensions
            bbox = obj.bbox
            xmin = int(bbox.xmin * scale_x)
            ymin = int(bbox.ymin * scale_y)
            xmax = int(bbox.xmax * scale_x)
            ymax = int(bbox.ymax * scale_y)

            # Draw the box
            draw.rectangle([(xmin, ymin), (xmax, ymax)], outline="red")

    if output:
        try:
            img.save(output)
        except IOError:
            print("Cannot save to output location.")
    
    return dict(detected_danger)




def main():
    # Set up test inputs
    model = "ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite"
    label = "coco_labels.txt"
    image = "person.jpg"  # Replace with the path to your test image
    output = "output_image.jpg"

    # Call the detect function
    detected_danger = detect(
        model=model,
        label=label,
        image=image,
        debug=True,
        output=output
    )

    # Print the results
    print("Detected danger items:")
    for item, count in detected_danger.items():
        print(f"{item}: {count}")

    print(f"Output image saved as: {output}")


if __name__ == "__main__":
    main()