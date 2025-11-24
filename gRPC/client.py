import cv2
import grpc
import time
import asyncio
import queue
from collections import deque

from gRPC.CloudRoute_pb2 import DetectionRequest
from gRPC.CloudRoute_pb2_grpc import CloudRouteStub, CloudRouteStub


def load_tls_credentials(cert_path):
    with open(cert_path, "rb") as f:
        trusted_cert = f.read()
    return grpc.ssl_channel_credentials(root_certificates=trusted_cert)


# ---------------------------
#   CAMERA CAPTURE THREAD
# ---------------------------

def camera_capture(send_queue, frame_buffer):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not found")
        return

    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame_id += 1
        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            continue

        # Save frame for later (match with detections)
        frame_buffer[frame_id] = frame.copy()

        # Push a DetectionRequest into queue
        send_queue.put(
            DetectionRequest(
                frame=encoded.tobytes(),
                width=frame.shape[1],
                height=frame.shape[0],
                frame_id=frame_id
            )
        )


# ---------------------------
#   ASYNC STREAM GENERATOR
# ---------------------------

async def async_request_stream(send_queue):
    while True:
        req = send_queue.get()   # blocking is fine (thread queue)
        yield req


# ---------------------------
#   ASYNC RECEIVER
# ---------------------------

async def receiver_loop(stub, request_stream, frame_buffer):
    responses = stub.CloudRouteStream(request_stream)

    last_time = time.time()

    async for response in responses:
        if response.frame_id not in frame_buffer:
            print("⚠️ Missing frame", response.frame_id)
            continue

        frame = frame_buffer.pop(response.frame_id)

        # Draw detections
        for det in response.detections:
            x1, y1 = int(det.x1), int(det.y1)
            x2, y2 = int(det.x2), int(det.y2)

            cv2.rectangle(frame, (x1, y1), (x2, y2),
                          (0, 255, 0), 2)
            cv2.putText(frame, f"{det.class_name} {det.confidence:.2f}",
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)

        # FPS
        now = time.time()
        fps = 1.0 / (now - last_time)
        last_time = now

        cv2.putText(frame, f"FPS: {fps:.2f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 0, 0), 2)

        cv2.imshow("Async Streaming", frame)

        if cv2.waitKey(1) == 27:
            break


# ---------------------------
#   MAIN ASYNC ENTRY
# ---------------------------

async def main_async():
    cert_path = "gRPC/server.crt"
    server = "localhost:50051"

    creds = load_tls_credentials(cert_path)

    async with grpc.aio.secure_channel(server, creds) as channel:
        stub = CloudRouteStub(channel)

        # Thread-safe frame queue
        send_queue = queue.Queue(maxsize=30)
        frame_buffer = {}

        # Start camera capture thread
        import threading
        threading.Thread(
            target=camera_capture,
            args=(send_queue, frame_buffer),
            daemon=True
        ).start()

        print("🚀 Starting FULLY ASYNC CloudRouteStream...")

        # Create async generator for outgoing frames
        request_stream = async_request_stream(send_queue)

        # Handle receiving and drawing
        await receiver_loop(stub, request_stream, frame_buffer)


# ---------------------------
#   MAIN
# ---------------------------

if __name__ == "__main__":
    asyncio.run(main_async())
