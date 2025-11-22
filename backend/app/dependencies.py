import os
import asyncio
from .api.schemas.thresholds import UIThresholds
from .core.use_cases.evaluate_suspicion import EvaluateSuspicionUseCase
from .core.services.suspicion.i_suspicion_service import ISuspicionService, SuspicionService
from .core.services.sse.i_server_side_events_service import IServerSideEventsService
from .core.use_cases.sse_connection import ServerSideEventsUseCase
from .core.services.sse.server_side_events import ServerSideEventsService
from .core.services.rabbitmqconsumer.rabbitmq_consumer import RabbitMQConsumer


ui_thresholds = UIThresholds(suspicion_score_threshold=70)
_suspicion_service = SuspicionService()
_sse_service = None  # will be initialized later

# Keep refs so GC doesn't cancel
_bg_tasks: list[asyncio.Task] = []
_consumer: RabbitMQConsumer | None = None


def _env(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v else default


async def init_dependencies(shutdown_event: asyncio.Event):
    global _sse_service, _consumer

    # 1) SSE singleton bound to the same shutdown signal
    _sse_service = ServerSideEventsService(shutdown_event)

    # 2) Define how to process incoming queue messages
    async def _on_queue_message(payload: dict):
        """
        Map queue message -> EvaluateSuspicionUseCase -> stream via SSE.
        Adjust 'execute'/'run' to whatever your use case method is named.
        """
        use_case = EvaluateSuspicionUseCase(
            suspicion_service=_suspicion_service,
            sse_service=_sse_service,
            threshold=ui_thresholds.suspicion_score_threshold,
        )

        # If your use case is sync, run it in thread; if it's async, await it directly.
        # Example assumes async:
        try:
            # Replace .execute(...) with your actual entrypoint (e.g., .run(...) / .handle(...))
            result = await use_case.execute(payload)  # <-- TODO: match your real method
        except AttributeError:
            # Fallback if your use case is sync
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, use_case.execute, payload)

        # Send a structured SSE event for the UI
        # Your SSEEventFactory should format this in to_sse_format()
        _sse_service.send_event("suspicion_result", result)

    # 3) Start RabbitMQ consumer
    _consumer = RabbitMQConsumer(
        amqp_url=_env("AMQP_URL", "amqp://guest:guest@rabbitmq:5672/"),
        queue_name=_env("AMQP_QUEUE", "guardcar.tasks"),
        on_message=_on_queue_message,
        prefetch=32,
        shutdown_event=shutdown_event,
    )
    task = asyncio.create_task(_consumer.run())
    _bg_tasks.append(task)


def get_suspicion_service() -> ISuspicionService:
    return _suspicion_service


def get_sse_service() -> IServerSideEventsService:
    return _sse_service


def get_suspicion_use_case():
    suspicion_service = get_suspicion_service()
    sse_service = get_sse_service()
    return EvaluateSuspicionUseCase(
        suspicion_service=suspicion_service,
        sse_service=sse_service,
        threshold=ui_thresholds.suspicion_score_threshold,
    )


def get_sse_use_case():
    sse_service = get_sse_service()
    return ServerSideEventsUseCase(sse_service=sse_service)
