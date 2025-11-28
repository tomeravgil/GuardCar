import base64
import os
from asyncio import Queue
import socket
from detection.model.yolo.yolo_detection import YOLODetectionService
from detection.processing.config_manager import ConfigManager
from detection.processing.processor_provider import ProcessorProvider
import logging
import requests
import cv2
import numpy as np
import struct
import httpx
import json
import threading
from detection.processing.processors.local_processor import LocalProcessor
from detection.processing.processors.rpc_processor import RPCProcessor
from detection.tracking.tracking_service import TrackingDetectionService
from gRPC.grpc_client import CloudClient
from rabbitMQ.consumer.connection_manager import ConnectionManager, Consumer, Producer
from rabbitMQ.dtos.dto import CloudProviderConfigMessage, SuspicionConfigMessage, RecordingStatusMessage, \
    SuspicionFrameMessage, ResponseMessage, VideoFrameMessage
import asyncio
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class DetectionManager:
    def __init__(self, model):
        self.processor_provider = ProcessorProvider()
        model_path = model if model is not None else "yolo11n.pt"
        self.yolo_detection_service = None
        self.tracking_service = TrackingDetectionService()
        self.config = ConfigManager()
        if self.config.get("CLASS_K"):
            raw_k = self.config.get("CLASS_K", {})

            # Convert keys back to int
            class_k = {int(k): float(v) for k, v in raw_k.items()}

            self.tracking_service.set_class_k(class_k)
        self._create_local_provider(model_path)
        self.video_ip = self.config.get("VIDEO_IP", "192.168.52.103")
        self.video_port = self.config.get("VIDEO_PORT", 8443)
        self.api_port = self.config.get("API_PORT", "8080")
        self.amqp_url = self.config.get("AMQP_URL", "amqp://guest:guest@localhost:5672/")
        self.connection_manager = ConnectionManager(self.amqp_url)
        self.event_queue = Queue()
        self.suspicion_score = self.config.get("SUSPICION_SCORE", 75)
        suspicion_frame_producer_queue_name = self.config.get("SUSPICION_FRAME_QUEUE_NAME", "SUSPICION_FRAME_QUEUE")
        recording_status_producer_queue_name = self.config.get("RECORDING_STATUS_QUEUE_NAME", "RECORDING_STATUS_QUEUE")
        response_queue_name = self.config.get("RESPONSE_QUEUE_NAME", "RESPONSE_QUEUE")
        frame_producer_queue_name = self.config.get("FRAME_QUEUE_NAME", "FRAME_QUEUE")
        self.frame_producer = Producer(frame_producer_queue_name)
        self.response_producer = Producer(response_queue_name)
        self.recording_producer = Producer(recording_status_producer_queue_name)
        self.suspicion_producer = Producer(suspicion_frame_producer_queue_name)
        self._register_queues()
        self.recording = False

    async def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info(f"Connecting to {self.video_ip}:{self.video_port} ...")

        try:
            s.connect((self.video_ip, self.video_port))
            logger.info("Connected! Receiving stream...")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return

        frame_id = 0
        try:
            while True:
                # 1. Read frame header
                header = self._receive_all(s, 4)
                if not header:
                    logger.warning("Stream ended.")
                    break

                frame_len = struct.unpack("!I", header)[0]

                # 2. Read JPEG payload
                jpg_bytes = self._receive_all(s, frame_len)
                if jpg_bytes is None:
                    logger.warning("Lost frame.")
                    break
                jpeg_b64 = base64.b64encode(jpg_bytes).decode()

                self.frame_producer.publish(message_obj=VideoFrameMessage(jpeg_bytes=jpeg_b64),expire_time="100")
                img = cv2.imdecode(np.frombuffer(jpg_bytes, np.uint8), cv2.IMREAD_COLOR)
                if img is None:
                    continue

                result = self.processor_provider.selected_provider.process(
                    resized_frame=img,
                    frame_id=frame_id
                )

                if asyncio.iscoroutine(result):
                    score, tracked = await result
                else:
                    score, tracked = result

                self.suspicion_producer.publish(
                    message_obj=SuspicionFrameMessage(
                        suspicion_score=score
                    ),
                    expire_time="100" # expire after 100ms
                )
                if score >= self.suspicion_score and not self.recording:
                    async with httpx.AsyncClient() as client:
                        await client.post(f"http://{self.video_ip}:{self.api_port}/start")
                    self.recording_producer.publish(RecordingStatusMessage(True))
                    self.recording = True
                elif score < self.suspicion_score and self.recording:
                    async with httpx.AsyncClient() as client:
                        await client.post(f"http://{self.video_ip}:{self.api_port}/stop")
                    self.recording_producer.publish(RecordingStatusMessage(False))
                    self.recording = False
                frame_id += 1
                await asyncio.sleep(0)
        except Exception as e:
            s.close()
            cv2.destroyAllWindows()
            logger.info(f"Stream ended: {e}")

    async def event_listener(self):
        while True:
            logger.info("starting event listener...")
            msg = await self.event_queue.get()  # WAITS — no polling
            await self._handle_event(msg)
            self.event_queue.task_done()

    async def _handle_event(self, msg):
        try:
            if isinstance(msg, CloudProviderConfigMessage):
                await self._handle_cloud_message(msg)
                return

            if isinstance(msg, SuspicionConfigMessage):
                self.suspicion_score = msg.threshold

                # Save permanently
                self.config.set("suspicion_score", msg.threshold)

                if isinstance(msg.class_weights, dict) and msg.class_weights:
                    class_k = {int(k): float(v) for k, v in msg.class_weights.items()}
                    self.tracking_service.set_class_k(class_k)
                    self.config.set("class_k", msg.class_weights)

                logger.info(f"Updated suspicion config: score={self.suspicion_score}")

                self.response_producer.publish(
                    ResponseMessage(
                        success=True,
                        message=f"Updated suspicion config!",
                        related_to="suspicion"
                    ),
                    expire_time="1000"
                )
                return

            logger.warning(
                f"Unknown message type received: {type(msg)} → {msg!r}"
            )
            self.response_producer.publish(
                ResponseMessage(
                    success=False,
                    message=f"Unsupported message type: {type(msg).__name__}",
                    related_to="general"
                ),
                expire_time="1000"
            )
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
            self.response_producer.publish(
                ResponseMessage(
                    success=False,
                    message=str(e),
                    related_to="general"
                ),
                expire_time="1000"
            )

    def _create_local_provider(self,model_path):
        """Ensures YOLO model exists, downloads if missing."""
        self._download_yolo(model_path)
        self.yolo_detection_service = YOLODetectionService(model_path)
        self.tracking_service = TrackingDetectionService()
        local_processor = LocalProcessor(detection_service=self.yolo_detection_service,
                                         tracking_service=self.tracking_service)
        self.processor_provider.register(name="local",provider=local_processor)

    def _download_yolo(self,model_path):
        if os.path.exists(model_path):
            return

        url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt"
        logger.info(f"Downloading YOLO model from {url}")

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(model_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        logger.info(f"Downloaded YOLO model to {model_path}")

    def _register_queues(self):
        cloud_provider_queue_name = self.config.get("CLOUD_PROVIDER_CONFIG_QUEUE_NAME","CLOUD_PROVIDER_CONFIG_QUEUE")
        suspicion_config_queue_name = self.config.get("SUSPICION_CONFIG_QUEUE_NAME", "SUSPICION_CONFIG_QUEUE")
        self.connection_manager.add_consumer(
            Consumer(cloud_provider_queue_name,self.event_queue, CloudProviderConfigMessage)
        )
        self.connection_manager.add_consumer(
            Consumer(suspicion_config_queue_name,self.event_queue, SuspicionConfigMessage)
        )
        self.connection_manager.add_producer(
            self.suspicion_producer
        )
        self.connection_manager.add_producer(
            self.recording_producer
        )
        self.connection_manager.add_producer(
            self.response_producer
        )
        self.connection_manager.add_producer(
            self.frame_producer
        )


    def _receive_all(self, sock, length):
        """Receive exactly `length` bytes from socket."""
        data = b''
        while len(data) < length:
            packet = sock.recv(length - len(data))
            if not packet:
                return None
            data += packet
        return data

    def start_video_thread(self):
        def wrapper():
            asyncio.run(self.run())  # THIS runs the async function properly

        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()

    async def _handle_cloud_message(self, msg: CloudProviderConfigMessage):
        if msg.delete:
            logger.info("Delete requested.")
            if msg.provider_name.lower() == "local":
                return

            # Find next provider and switch FIRST
            await self._delete_provider(msg.provider_name)
            self.config.remove_provider(msg.provider_name)
            self.response_producer.publish(
                ResponseMessage(
                    success=True,
                    message=f"Deleted provider {msg.provider_name}",
                    related_to="cloud"
                ),
                expire_time="1000"
            )
            return
        try:
            cloud = CloudClient(server=msg.connection_ip, cert_path=msg.server_certification,
                                loop=asyncio.get_running_loop())
            asyncio.create_task(cloud.start())
            await asyncio.wait_for(cloud.connected.wait(), timeout=5)
            logger.info("Cloud gRPC connected.")
            rpc_processor = RPCProcessor(local_detection_service=self.yolo_detection_service,
                                         cloud_client=cloud,
                                         tracking_service=self.tracking_service)
            self.processor_provider.register(name="cloud", provider=rpc_processor)
            self.processor_provider.change_main_provider(name="cloud")
            self.config.add_provider(msg.provider_name, {
                "type": "cloud",
                "connection_ip": msg.connection_ip,
                "server_certification": msg.server_certification,
                "active": True
            })
            self.response_producer.publish(
                ResponseMessage(
                    success=True,
                    message=f"Added provider {msg.provider_name}",
                    related_to="cloud"
                ),
                expire_time="1000"
            )
        except asyncio.TimeoutError:
            logger.warning("Cloud gRPC timeout — continuing without cloud.")
            await self._delete_provider(msg.provider_name)
            self.config.remove_provider(msg.provider_name)


    async def _delete_provider(self,provider_name):
        next_provider = self.processor_provider.find_next_cloud_provider(provider_name)
        logger.info(f"Switching to next provider: {next_provider}")
        self.processor_provider.change_main_provider(name=next_provider)

        # THEN remove (and stop) the old one
        await self.processor_provider.remove_provider(name=provider_name)
