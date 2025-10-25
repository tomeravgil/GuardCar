from core.services.sse.events.events import SSEEvent


class TestSSEEvent(SSEEvent):
    """Concrete implementation of SSEEvent for testing."""

    def validate_event(self) -> bool:
        """Validate the event data for testing."""
        if not isinstance(self.data, dict):
            return False
        if not self.event:
            return False
        return True
