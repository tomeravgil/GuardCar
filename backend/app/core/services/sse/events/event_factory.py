from marshmallow import ValidationError

from rabbitMQ.dtos.dto import RecordingStatusMessage
from ..events.events_impl import *


class SSEEventFactory:
    EVENT_MAP = {
        "suspicion": SuspicionDetected,
        "success": SuccessResponseEvent,
        "error": FailureResponseEvent,
        "recording" : RecordingStatusMessage,
        "multi_test": MultiTestEvent,
        "test_event": TestEvent
    }

    @classmethod
    def create_event(cls, event_type: str, data: dict) -> SSEEventImpl:
        event_class = cls.EVENT_MAP.get(event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")
        event_instance = event_class(event=event_type, data=data)
        try:
            event_instance.validate_event()
        except ValidationError as e:
            raise e
        return event_instance
