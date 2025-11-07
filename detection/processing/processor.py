import cv2
import pybreaker

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

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Can't receive frame. Exiting...")
                    break

                frame_bytes = cv2.imencode('.jpg', frame)[1].tobytes()

                # ---- Circuit Breaker Protected RF Call ----
                try:
                    result = self.circuit_breaker.call(
                        self.rf_detection_service.detect,
                        frame_bytes
                    )
                except pybreaker.CircuitBreakerError:
                    # Circuit breaker is OPEN → Skip remote call entirely
                    print("[CB OPEN] Falling back to YOLO")
                    result = self.yolo_detection_service.detect(frame_bytes)
                except Exception:
                    # A failure occurred → record & fallback
                    print("[RF FAIL] Falling back to YOLO")
                    result = self.yolo_detection_service.detect(frame_bytes)

                # Update tracking with detection results
                # tracked_objects = self.tracking_service.process_frame(result)
                
                # Draw bounding boxes and track IDs
                print(result)
                # for box in result.boxes:
                #     x1, y1, x2, y2 = map(int, box.xyxy[0])
                #     track_id = int(box.id[0]) if box.id is not None else -1
                    
                #     # Draw bounding box
                #     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                #     # Draw track ID
                #     cv2.putText(frame, f'ID: {track_id}', (x1, y1 - 10), 
                #                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Display tracking score in the top-left corner
                # cv2.putText(frame, f'Tracking Score: {tracked_objects:.2f}', (10, 30), 
                #           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                cv2.imshow('Camera Feed', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("\nVideo capture stopped by user.")

        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("Video capture resources released.")
