import grpc
import asyncio
from gRPC.CloudRoute_pb2_grpc import CloudRouteStub
from gRPC.CloudRoute_pb2 import DetectionRequest
import cv2
import logging
logger = logging.getLogger(__name__)

class GRPCClient:
    def __init__(self, server, cert_path):
        self.server = server
        self.credentials = self._load_tls_credentials(cert_path)
        self.connected = asyncio.Event()
        self.channel = None
        self.stub = None

    def _load_tls_credentials(self, cert):
        with open(cert, "rb") as f:
            trusted_cert = f.read()
        return grpc.ssl_channel_credentials(root_certificates=trusted_cert)

    def connect(self):
        try:
            self.channel = grpc.aio.secure_channel(self.server, self.credentials)
            self.stub = CloudRouteStub(self.channel)
            self.connected.set()
        except Exception as e:
            logger.error("Failed to connect to gRPC server: %s", e)
            raise e

class CloudClient(GRPCClient):
    def __init__(self, server, cert_path):
        super().__init__(server, cert_path)
        self.send_queue = asyncio.Queue(maxsize=30)
        self.frame_buffer = {}
        self.processed_frames = {}
        self.frame_events = {}

    async def send_frame(self, frame, frame_id):
        if not self.connected.is_set():
            raise Exception("Connection lost")
        self.frame_buffer[frame_id] = frame.copy()
        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            raise Exception("Failed to encode frame")
        await self.send_queue.put(
            DetectionRequest(
                frame=encoded.tobytes(),
                width=frame.shape[1],
                height=frame.shape[0],
                frame_id=frame_id
            )
        )
    
    async def _request_stream(self):
        while True:
            req = await self.send_queue.get()
            yield req
    
    async def start(self):
        while True:
            try:
                logger.info("Starting gRPC client")
                self.connect()
                logger.info("Starting FULLY ASYNC CloudRouteStream...")
                responses = self.stub.CloudRouteStream(self._request_stream())
                async for response in responses:
                    if response.frame_id not in self.frame_buffer:
                        logger.warning("Missing frame %s", response.frame_id)
                        continue
                    frame = self.frame_buffer.pop(response.frame_id)
                    self.processed_frames[response.frame_id] = (response, frame)
                    if response.frame_id in self.frame_events:
                        self.frame_events[response.frame_id].set()
            except Exception as e:
                logger.error(f"CloudClient error: {e}")
                self.connected.clear()
                await self.clear_queue()
                logger.info("Reconnecting in 2 seconds...")
                await asyncio.sleep(2)
                
    async def get_processed_frame(self, frame_id, timeout=0.2):
        if frame_id in self.processed_frames:
            return self.processed_frames[frame_id]

        # Create event if necessary
        if frame_id not in self.frame_events:
            self.frame_events[frame_id] = asyncio.Event()

        try:
            await asyncio.wait_for(self.frame_events[frame_id].wait(), timeout)
        except asyncio.TimeoutError:
            return None

        return self.processed_frames.get(frame_id)

    async def clear_queue(self):
        await self._clear_asyncio_queue()
        self.frame_buffer.clear()
        self.processed_frames.clear()

    async def _clear_asyncio_queue(self):
        while not self.send_queue.empty():
            try:
                await self.send_queue.get()
                self.send_queue.task_done()
            except asyncio.QueueEmpty:
                break


