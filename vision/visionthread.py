import threading
from ultralytics import YOLO
import cv2

class VisionThread(threading.Thread):
    """
    A thread class that captures video from a webcam and performs object detection
    using a YOLO model in real-time.
    
    Attributes:
        frame_count (int): A counter for the number of frames processed.
        model (YOLO): The YOLO model used for object detection.
    """
    
    def __init__(self):
        """
        Initializes the VisionThread, setting up the YOLO model for object detection
        and preparing to capture video from the webcam.
        """
        super().__init__()
        self.frame_count = 0
        self.model = YOLO('yolov5nu.pt')  # Initialize the YOLO model. Ensure the path is correct.

    def run(self):
        """
        The main execution of the thread, which starts the video recording and object detection process.
        """
        self.record()

    def record(self):
        """
        Opens the default webcam and captures video frames. Each frame is processed using
        the YOLO model for object detection, and the results are displayed in real-time.
        """
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

                # Perform object detection on the frame
                results = self.model.predict(frame, imgsz=320)  # Set image size to 320x320 for faster processing
                print(results[0])  # Print detection results

                # Annotate the frame with bounding boxes and labels
                annotated_frame = results[0].plot()

                # Print frame shape for debugging purposes
                print(f"Annotated Frame Shape: {annotated_frame.shape}")

                # Display the frame with YOLO detections
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
