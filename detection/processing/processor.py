import cv2
import pybreaker
import time
import json
class Processor:
    def __init__(self, yolo_detection_service, rf_detection_service, tracking_service):
        self.yolo_detection_service = yolo_detection_service
        self.rf_detection_service = rf_detection_service
        self.tracking_service = tracking_service

        self.circuit_breaker = pybreaker.CircuitBreaker(
            fail_max=3,        
            reset_timeout=5      
        )

    def start_video_processing(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return
        
        print("Starting video capture. Press 'q' to quit...")
        prev_time = time.time()

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Can't receive frame. Exiting...")
                    break

                # --- Resize before sending ---
                resized = cv2.resize(frame, (640, 640))
                frame_bytes = cv2.imencode('.jpg', resized)[1].tobytes()

                try:
                    result = self.circuit_breaker.call(
                        self.rf_detection_service.detect,
                        frame_bytes
                    )
                except pybreaker.CircuitBreakerError:
                    print("[CB OPEN] Falling back to YOLO")
                    result = self.yolo_detection_service.detect(frame_bytes)
                except Exception:
                    print("[RF FAIL] Falling back to YOLO")
                    result = self.yolo_detection_service.detect(resized)

                # Parse detection output safely
                if isinstance(result, str):
                    try:
                        result = json.loads(result)
                    except:
                        result = []

                # --- Scale detections back to original frame size ---
                h, w = frame.shape[:2]
                scale_x = w / 640
                scale_y = h / 640

                for det in result:
                    x1, y1, x2, y2 = det["bbox"]
                    x1 = int(x1 * scale_x)
                    y1 = int(y1 * scale_y)
                    x2 = int(x2 * scale_x)
                    y2 = int(y2 * scale_y)

                    cls = det.get("class", "object")
                    conf = det.get("confidence", 0)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{cls} {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # FPS calculation
                current_time = time.time()
                fps = 1 / (current_time - prev_time)
                prev_time = current_time

                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                cv2.imshow('Camera Feed', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


        except KeyboardInterrupt:
            print("\nVideo capture stopped by user.")

        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("Video capture resources released.")
