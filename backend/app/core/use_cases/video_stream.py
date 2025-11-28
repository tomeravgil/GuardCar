import asyncio
import cv2
import numpy as np
from asyncio import Queue
import base64

class VideoStreamUseCase:
    """
    Now the UseCase does NOT connect to the Pi.

    • Detection container sends frames via RMQ (base64 JPEG)
    • RMQ consumer calls inject_frame(jpeg_bytes)
    • This class fan-outs frames to all subscribed WS clients
    """

    def __init__(self):
        self.subscribers: list[Queue] = []

    # ---------------------------------------------------------
    # Subscriber Management
    # ---------------------------------------------------------
    def subscribe(self) -> Queue:
        q = Queue(maxsize=1)
        self.subscribers.append(q)
        return q

    def unsubscribe(self, q: Queue):
        if q in self.subscribers:
            self.subscribers.remove(q)

    # ---------------------------------------------------------
    # New method: backend injects JPEG frames into this
    # ---------------------------------------------------------
    def inject_frame(self, jpeg_bytes: bytes):
        """
        Called by RabbitMQ event handler when a new frame arrives.
        This fan-outs the frame to all subscribers.
        """
        for q in list(self.subscribers):
            if not q.full():  # drop old frame if subscriber is slow
                q.put_nowait(jpeg_bytes)

    # ---------------------------------------------------------
    # Frame processing helpers
    # ---------------------------------------------------------
    @staticmethod
    def split_frame(jpeg_bytes):
        arr = np.frombuffer(jpeg_bytes, dtype=np.uint8)
        full = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        cam0 = full[:, :640, :]
        cam1 = full[:, 640:, :]
        return cam0, cam1

    @staticmethod
    def encode_jpeg(img, quality=85):
        ok, out = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        return out.tobytes() if ok else None
