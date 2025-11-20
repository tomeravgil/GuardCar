from app.core.services.sse.events.events_impl import SSEEventImpl


class SSEEventFactory:
    EVENT_MAP = {
        "event": SSEEventImpl,
        "suspicion_detected": SSEEventImpl,
        "clear": SSEEventImpl,
        "warning": SSEEventImpl,
        "info": SSEEventImpl,
        "error": SSEEventImpl,
        "multi_test": SSEEventImpl,
        "test_event": SSEEventImpl,
    }

    @classmethod
    def create_event(cls, event_type: str, data: dict) -> SSEEventImpl:
        event_class = cls.EVENT_MAP.get(event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")
        event_instance = event_class(event=event_type, data=data)
        return event_instance
