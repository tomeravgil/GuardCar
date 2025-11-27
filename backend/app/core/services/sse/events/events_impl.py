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


class ClearEvent(SSEEventImpl):
    """Event indicating state has returned to normal."""

    def _validate_specific(self) -> bool:
        # Dictionary[str, str]
        return self._has_str_keys_and_values_of_type(str)


class WarningEvent(SSEEventImpl):
    """Non-fatal warning event."""

    def _validate_specific(self) -> bool:
        # Dictionary[str, str]
        return self._has_str_keys_and_values_of_type(str)


class InfoEvent(SSEEventImpl):
    """Informational event."""

    def _validate_specific(self) -> bool:
        # Dictionary[str, str]
        return self._has_str_keys_and_values_of_type(str)


class ErrorEvent(SSEEventImpl):
    """Error event for downstream consumers."""

    def _validate_specific(self) -> bool:
        # Dictionary[str, str]
        if not self._has_str_keys_and_values_of_type(str):
            return False

        # Still enforce required keys
        if "message" not in self.data:
            return False
        if "error_code" not in self.data:
            return False

        return True


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
