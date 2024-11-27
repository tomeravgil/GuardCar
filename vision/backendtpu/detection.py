# from edgetpu.detection.engine import DetectionEngine
# from edgetpu.utils import dataset_utils
# from PIL import Image
# from PIL import ImageDraw

# def detect(model="ssd_mobilenet_v2_coco_quant_postprocess_edgetpu.tflite",
#            label="coco_labels.txt",
#            image="",
#            debug="True",
#            output=""):
    
#     #error checking for image
#     if image == "":
#         print("No image sent")
#         return
    
#     #initialize engine

#     engine = DetectionEngine(model)
#     labels = dataset_utils.read_label_file(label)

#     img = Image.open(image).convert('RGB')


#     objs = engine.detect_with_image(img,
#                                     threshold=0.5,
#                                     relative_coord=False,
#                                     top_k=5)

#     if not debug:
#         danger_list = ["person","bicycle","car","motorcycle","truck","backpack","baseball bat","bottle","knife", "fork", "chair"]
#         detected_danger = dict()
#         for obj in objs:
#             obj_label = labels[obj.label_id]
#             if obj_label in danger_list:
#                 detected_danger[obj_label] += 1
#         return detected_danger
    

#     draw = ImageDraw.Draw(img)
#     danger_list = ["person","bicycle","car","motorcycle","truck","backpack","baseball bat","bottle","knife", "fork", "chair"]
#     detected_danger = dict()
#     for obj in objs:
#         obj_label = labels[obj.label_id]
#         if obj_label in danger_list:
#             detected_danger[obj_label] += 1
#             box = obj.bounding_box.flatten().tolist()
#             draw.rectangle(box,outline="red")
    
#     try:
#         image.save(output)
#     except IOError:
#         print("cannot save to output location")

#     return detected_danger

                
from pycoral.adapters.detect import get_objects
from pycoral.utils.edgetpu import make_interpreter
from pycoral.utils.dataset import read_label_file
from PIL import Image, ImageDraw
from collections import defaultdict

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
    _, scale = interpreter.input_details[0]['shape'][1:3], interpreter.input_details[0]['shape'][2]

    # Preprocess the image
    resized_img = img.resize((scale, scale))
    input_tensor = input_tensor(interpreter)
    input_tensor[:, :] = resized_img

    # Run inference
    interpreter.invoke()
    objs = get_objects(interpreter, threshold=0.5)

    danger_list = ["person", "bicycle", "car", "motorcycle", "truck", "backpack", 
                   "baseball bat", "bottle", "knife", "fork", "chair"]
    detected_danger = defaultdict(int)

    if not debug:
        for obj in objs:
            obj_label = labels.get(obj.id, obj.id)
            if obj_label in danger_list:
                detected_danger[obj_label] += 1
        return dict(detected_danger)

    draw = ImageDraw.Draw(img)
    for obj in objs:
        obj_label = labels.get(obj.id, obj.id)
        if obj_label in danger_list:
            detected_danger[obj_label] += 1
            bbox = obj.bbox
            draw.rectangle([(bbox.xmin, bbox.ymin), (bbox.xmax, bbox.ymax)], outline="red")

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
    image = "test_image.jpg"  # Replace with the path to your test image
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