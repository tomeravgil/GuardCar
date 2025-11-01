from detection import TrackingDetectionService
import os,subprocess

def main():

    # fetch model name if it is defined in runtime env variables
    model_name = os.getenv("MODEL_NAME","yolo11.pt")
    model_url = os.getenv("MODEL_URL","https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt")
    test_env = os.getenv("TEST_ENV", "false").lower() in ("true", "1", "yes")

    # download model if it is not already downloaded
    if not os.path.exists(model_name):
        print(f"Downloading model {model_name} from {model_url}...")
        subprocess.run(["curl", "-L", "-o", model_name, model_url], check=True)

    if test_env:
        print("Running in test environment")
        # put test service here 
        return
    

    tracking_detection_service = TrackingDetectionService(model_name, "streaming_urls.txt")
    
    tracking_detection_service.detect_and_process()


if __name__ == "__main__":
    main()
    