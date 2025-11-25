import grpc
import asyncio
from gRPC.CloudRoute_pb2_grpc import CloudRouteStub
from gRPC.CloudRoute_pb2 import DetectionRequest
import cv2
import logging
import base64
logger = logging.getLogger(__name__)

import re

def normalize_address(addr: str) -> str:
    # detect IPv6
    if ":" in addr and addr.count(":") > 1:
        if "[" not in addr:
            host, port = addr.rsplit(":", 1)
            return f"[{host}]:{port}"
    return addr

class GRPCClient:
    def __init__(self, server, cert_path):
        self.server = normalize_address(server)
        der_bytes = base64.b64decode(cert_path)
        pem = (
                b"-----BEGIN CERTIFICATE-----\n" +
                base64.encodebytes(der_bytes) +
                b"-----END CERTIFICATE-----\n"
        )
        self.credentials = grpc.ssl_channel_credentials(root_certificates=pem)
        self.connected = asyncio.Event()
        self.channel = None
        self.stub = None

    async def connect(self):
        logger.info(f"Connecting to gRPC at {self.server}...")
        try:
            self.channel = grpc.aio.secure_channel(self.server, self.credentials)
            self.stub = CloudRouteStub(self.channel)

            # WAIT FOR TLS handshake + TCP ready
            await self.channel.channel_ready()

            logger.info("gRPC channel ready.")
            self.connected.set()

        except Exception as e:
            logger.error(f"Failed to connect to gRPC server: {e}")
            raise

class CloudClient(GRPCClient):
    def __init__(self, server, cert_path, loop=None):
        super().__init__(server, cert_path)
        self.loop = loop if loop else asyncio.get_running_loop()
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
                await self.connect()
                logger.info("Starting FULLY ASYNC CloudRouteStream...")
                request_stream = self._request_stream()
                responses = self.stub.CloudRouteStream(request_stream)
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
