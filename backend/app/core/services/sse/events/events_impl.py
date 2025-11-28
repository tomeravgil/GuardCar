from ..events.events import SSEEvent

class SSEEventImpl(SSEEvent):
    """Base implementation with shared validation logic."""

    def validate_event(self) -> bool:
        """Template method: common checks + per-event specifics."""
        if not isinstance(self.data, dict):
            return False

        if not getattr(self, "event", None):
            return False

        # ---- subclass-specific validation ----
        return self._validate_specific()

    def _validate_specific(self) -> bool:
        """
        Hook for subclasses to override.
        Default is 'no extra validation'.
        """
        return True

    def _has_str_keys_and_values_of_type(self, value_types) -> bool:
        """
        Ensure data is a dict[str, value_types].
        value_types can be a single type or a tuple of types.
        """
        for key, value in self.data.items():
            if not isinstance(key, str):
                return False
            if not isinstance(value, value_types):
                return False
        return True

# --------------------- Concrete Event Types ---------------------
class SuspicionDetected(SSEEventImpl):
    """Event for when a suspicion score crosses a threshold."""

    def _validate_specific(self) -> bool:
        if not self._has_str_keys_and_values_of_type((int, float)):
            return False

        score = self.data.get("suspicion_score")
        return isinstance(score, (int, float))


class RecordingEvent(SSEEventImpl):
    """SSE event indicating whether the Pi is recording."""

    def _validate_specific(self) -> bool:
        # Must contain: {"recording": bool}
        if not self._has_str_keys_and_values_of_type(bool):
            return False

        return "recording" in self.data


class SuccessResponseEvent(SSEEventImpl):
    """SSE event emitted when a ResponseMessage indicates success."""

    def _validate_specific(self) -> bool:
        # required keys
        if "success" not in self.data or "message" not in self.data or "related_to" not in self.data:
            return False

        # ensure correct types
        if not isinstance(self.data["success"], bool):
            return False
        if not isinstance(self.data["message"], str):
            return False
        if self.data["related_to"] not in ("cloud", "suspicion", "general"):
            return False

        # final check: this event only when success=True
        return self.data["success"] is True


class FailureResponseEvent(SSEEventImpl):
    """SSE event emitted when a ResponseMessage indicates failure."""

    def _validate_specific(self) -> bool:
        # required keys
        if "success" not in self.data or "message" not in self.data or "related_to" not in self.data:
            return False

        # ensure correct types
        if not isinstance(self.data["success"], bool):
            return False
        if not isinstance(self.data["message"], str):
            return False
        if self.data["related_to"] not in ("cloud", "suspicion", "general"):
            return False

        # final check: this event only when success=False
        return self.data["success"] is False

class MultiTestEvent(SSEEventImpl):
    """Event used for multi-test / dev scenarios."""

    def _validate_specific(self) -> bool:
        # Dictionary[str, bool]
        return self._has_str_keys_and_values_of_type(bool)


class TestEvent(SSEEventImpl):
    """Simple test/heartbeat event."""

    def _validate_specific(self) -> bool:
        # Dictionary[str, bool]
        return self._has_str_keys_and_values_of_type(bool)
