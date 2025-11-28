import os
import asyncio
from .api.schemas.thresholds import UIThresholds
from .core.use_cases.cloud_config import CloudConfigurationConfigurationUseCase
from .core.use_cases.evaluate_suspicion import EvaluateSuspicionUseCase
from .core.services.suspicion.i_suspicion_service import ISuspicionService, SuspicionService
from .core.services.sse.i_server_side_events_service import IServerSideEventsService
from .core.use_cases.sse_connection import ServerSideEventsUseCase
from .core.services.sse.server_side_events import ServerSideEventsService
from .core.services.rabbitmqconsumer.rabbitmq_consumer import RabbitMQEventHandler
from rabbitMQ.consumer.connection_manager import ConnectionManager, Consumer, Producer
from rabbitMQ.dtos.dto import SuspicionFrameMessage, RecordingStatusMessage, ResponseMessage, VideoFrameMessage
from asyncio import Queue

from .core.use_cases.suspicion_config import SuspicionConfigurationUseCase
from .core.use_cases.video_stream import VideoStreamUseCase

ui_thresholds = UIThresholds(suspicion_score_threshold=70)
_suspicion_service = SuspicionService()

# will be initialized later
_sse_service = None

# Keep refs so GC doesn't cancel
_bg_tasks: list[asyncio.Task] = []
_connection_manager: RabbitMQEventHandler | None = None
_producers = []
_video_stream_use_case: VideoStreamUseCase | None = None

def _env(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v else default

def init_dependencies(shutdown_event: asyncio.Event):
    global _sse_service, _connection_manager, _producers, _video_stream_use_case

    loop = asyncio.get_running_loop()  # now safe: called from startup event

    # 1) SSE service
    _sse_service = ServerSideEventsService(shutdown_event)

    _video_stream_use_case = VideoStreamUseCase()

    # 2) Shared event queue
    event_queue: Queue = Queue()

    # 3) Connection manager wired to this loop
    _connection_manager = ConnectionManager(
        amqp_url=_env("AMQP_URL", "amqp://guest:guest@localhost:5672/"),
        asyncio_loop=loop,
    )

    suspicion_consumer = Consumer("SUSPICION_FRAME_QUEUE", event_queue, SuspicionFrameMessage)
    recording_status_consumer = Consumer("RECORDING_STATUS_QUEUE", event_queue, RecordingStatusMessage)
    response_consumer = Consumer("RESPONSE_QUEUE", event_queue, ResponseMessage)
    frame_consumer = Consumer("FRAME_QUEUE",event_queue, VideoFrameMessage)
    consumers = [suspicion_consumer, recording_status_consumer, response_consumer, frame_consumer]

    cloud_provider_config_queue = Producer("CLOUD_PROVIDER_CONFIG_QUEUE")
    suspicion_config_queue = Producer("SUSPICION_CONFIG_QUEUE")
    _producers = [cloud_provider_config_queue, suspicion_config_queue]

    for consumer in consumers:
        _connection_manager.add_consumer(consumer)
    for producer in _producers:
        _connection_manager.add_producer(producer)

    # 4) Start RabbitMQ connection in its own thread
    _connection_manager.run_in_background()

    # 5) Start async RabbitMQ → SSE bridge in the event loop
    handler = RabbitMQEventHandler(event_queue, _sse_service, _video_stream_use_case, shutdown_event)
    task = asyncio.create_task(handler.run())
    _bg_tasks.append(task)


def get_suspicion_service() -> ISuspicionService:
    return _suspicion_service


def get_sse_service() -> IServerSideEventsService:
    return _sse_service

def get_producers() -> list[Producer]:
    return _producers

def get_suspicion_use_case():
    suspicion_service = get_suspicion_service()
    sse_service = get_sse_service()
    return EvaluateSuspicionUseCase(
        suspicion_service=suspicion_service,
        sse_service=sse_service,
        threshold=ui_thresholds.suspicion_score_threshold,
    )

def get_suspicion_config_use_case():
    suspicion_config_producer = get_producers()[1]
    return SuspicionConfigurationUseCase(suspicion_config_producer=suspicion_config_producer)

def get_cloud_provider_config_use_case():
    cloud_provider_config_producer = get_producers()[0]
    return CloudConfigurationConfigurationUseCase(
        cloud_config_producer=cloud_provider_config_producer)

def get_sse_use_case():
    sse_service = get_sse_service()
    return ServerSideEventsUseCase(sse_service=sse_service)

def get_video_stream_use_case() -> VideoStreamUseCase:
    return _video_stream_use_case
