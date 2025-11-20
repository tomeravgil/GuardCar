from app.core.services.sse.events.events import SSEEvent


class SSEEventImpl(SSEEvent):
    """Concrete implementation of SSEEvent for the event factory."""

    def validate_event(self) -> bool:
        """Validate the event data."""
        if not isinstance(self.data, dict):
            return False
        if not self.event:
            return False
        return True
