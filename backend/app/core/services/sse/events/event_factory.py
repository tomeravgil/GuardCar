from core.services.sse.events.events import SSEEvent


class SSEEventFactory:
    EVENT_MAP = {
        "event" : SSEEvent,
    }

    @classmethod
    def create_event(cls, event_type: str, data: dict) -> SSEEvent:
        event_class = cls.EVENT_MAP.get(event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")
        event_instance = event_class(event=event_type, data=data)
        return event_instance
