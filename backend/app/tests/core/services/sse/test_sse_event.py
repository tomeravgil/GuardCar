import pytest
from unittest.mock import Mock
from core.services.sse.events.events import SSEEvent


class ConcreteSSEEvent(SSEEvent):
    """Concrete implementation of SSEEvent for testing."""

    def validate_event(self) -> bool:
        """Simple validation for testing."""
        return isinstance(self.data, dict) and bool(self.event)


class TestSSEEvent:
    """Test cases for the SSEEvent class."""

    def test_sse_event_creation(self, sample_event_data):
        """Test creating an SSEEvent instance."""
        event = ConcreteSSEEvent(event="test_event", data=sample_event_data)

        assert event.event == "test_event"
        assert event.data == sample_event_data

    def test_to_sse_format_valid_event(self, sample_event_data):
        """Test converting event to SSE format with valid data."""
        event = ConcreteSSEEvent(event="test_event", data=sample_event_data)
        sse_string = event.to_sse_format()

        expected_data = '{"id": "test-123", "type": "suspicion_detected", "timestamp": "2024-01-01T12:00:00Z", "confidence": 0.85, "details": "Suspicious activity detected"}'
        expected = f"event: test_event\ndata: {expected_data}\n\n"

        assert sse_string == expected

    def test_to_sse_format_with_simple_data(self):
        """Test converting event to SSE format with simple data."""
        simple_data = {"message": "Hello World"}
        event = ConcreteSSEEvent(event="greeting", data=simple_data)
        sse_string = event.to_sse_format()

        expected = 'event: greeting\ndata: {"message": "Hello World"}\n\n'
        assert sse_string == expected

    def test_to_sse_format_with_empty_data(self):
        """Test converting event to SSE format with empty data."""
        event = ConcreteSSEEvent(event="empty", data={})
        sse_string = event.to_sse_format()

        expected = "event: empty\ndata: {}\n\n"
        assert sse_string == expected

    def test_to_sse_format_with_special_characters(self):
        """Test converting event to SSE format with special characters."""
        data_with_specials = {
            "message": "Hello\nWorld",
            "quote": 'He said "hello"',
            "unicode": "café"
        }
        event = ConcreteSSEEvent(event="special", data=data_with_specials)
        sse_string = event.to_sse_format()

        # JSON should properly escape special characters
        assert "Hello\\nWorld" in sse_string
        assert '\\"hello\\"' in sse_string
        assert "caf\\u00e9" in sse_string

    def test_validate_event_valid(self, sample_event_data):
        """Test validation with valid event data."""
        event = ConcreteSSEEvent(event="valid_event", data=sample_event_data)
        assert event.validate_event() is True

    def test_validate_event_invalid_data_type(self):
        """Test validation with invalid data type."""
        event = ConcreteSSEEvent(event="invalid", data="not a dict")
        assert event.validate_event() is False

    def test_validate_event_empty_event(self):
        """Test validation with empty event name."""
        event = ConcreteSSEEvent(event="", data={"valid": "data"})
        assert event.validate_event() is False

    def test_validate_event_none_data(self):
        """Test validation with None data."""
        event = ConcreteSSEEvent(event="none_data", data=None)
        assert event.validate_event() is False

    def test_sse_event_immutable_fields(self):
        """Test that event fields are properly set and accessible."""
        data = {"test": "value"}
        event = ConcreteSSEEvent(event="immutable_test", data=data)

        # Test that fields are accessible
        assert event.event == "immutable_test"
        assert event.data == data

        # Test that data is the same object (shallow copy)
        assert event.data is data

    def test_sse_format_structure(self):
        """Test that SSE format follows the correct structure."""
        event = ConcreteSSEEvent(event="structure_test", data={"key": "value"})
        sse_string = event.to_sse_format()

        # Check that it starts with event line
        lines = sse_string.strip().split('\n')
        print(lines)
        assert lines[0].startswith("event: ")
        assert lines[1].startswith("data: ")
        # Check that event name is correct
        assert "structure_test" in lines[0]

        # Check that data is JSON formatted
        assert '{"key": "value"}' in lines[1]
