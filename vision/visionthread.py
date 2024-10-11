import threading
from ultralytics import YOLO
import cv2

class VisionThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.frame_count = 0
        self.model = YOLO('yolov5nu.pt')  # Make sure this path is correct

    def run(self):
        self.record()

    def record(self):
        # Open a connection to the webcam (0 is typically the default webcam)
        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            print("Error: Could not open video stream from webcam.")
            return

        try:
            while True:
                # Read a frame from the camera
                ret, frame = camera.read()
                if not ret:
                    print("Error: Failed to capture image.")
                    break

                # Perform object detection
                results = self.model.predict(frame, imgsz=320)  # Set image size to 320x320
                print(results[0])
                # Plot the results on the frame
                annotated_frame = results[0].plot()

                # Print frame shape for debugging
                print(f"Annotated Frame Shape: {annotated_frame.shape}")

                # Display the frame with bounding boxes
                # cv2.imshow('YOLOv8 Nano - Object Detection', annotated_frame)

                # Break the loop if the user presses 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            # Release the camera and close any OpenCV windows
            camera.release()
            cv2.destroyAllWindows()


# Instantiate and start the vision thread
vision_thread = VisionThread()
vision_thread.start()

# Optionally, you can later join the thread
vision_thread.join()
