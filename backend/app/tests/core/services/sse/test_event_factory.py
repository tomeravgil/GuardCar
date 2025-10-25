import pytest
from unittest.mock import patch
from core.services.sse.events.event_factory import SSEEventFactory


class TestSSEEventFactory:
    """Test cases for the SSEEventFactory class."""

    def test_create_event_valid_type(self, sample_event_data):
        """Test creating an event with a valid event type."""
        event = SSEEventFactory.create_event("event", sample_event_data)

        assert event.event == "event"
        assert event.data == sample_event_data
        assert hasattr(event, 'validate_event')
        assert hasattr(event, 'to_sse_format')

    def test_create_event_with_empty_data(self):
        """Test creating an event with empty data."""
        event = SSEEventFactory.create_event("event", {})

        assert event.event == "event"
        assert event.data == {}

    def test_create_event_with_complex_data(self):
        """Test creating an event with complex nested data."""
        complex_data = {
            "nested": {
                "key": "value",
                "list": [1, 2, 3]
            },
            "timestamp": "2024-01-01T12:00:00Z"
        }
        event = SSEEventFactory.create_event("event", complex_data)

        assert event.event == "event"
        assert event.data == complex_data

    def test_create_event_unknown_type(self):
        """Test creating an event with an unknown event type."""
        with pytest.raises(ValueError, match="Unknown event type: unknown_event"):
            SSEEventFactory.create_event("unknown_event", {"data": "test"})

    def test_create_event_case_sensitive(self):
        """Test that event type matching is case sensitive."""
        # Add a new event type temporarily
        original_map = SSEEventFactory.EVENT_MAP.copy()
        try:
            SSEEventFactory.EVENT_MAP["EVENT"] = SSEEventFactory.EVENT_MAP["event"]

            # Should work with exact case
            event1 = SSEEventFactory.create_event("event", {"test": "data"})
            assert event1.event == "event"

            # Should work with uppercase since we explicitly added it
            event2 = SSEEventFactory.create_event("EVENT", {"test": "data"})
            assert event2.event == "EVENT"

            # Should still fail with a truly unknown type
            with pytest.raises(ValueError, match="Unknown event type: UNKNOWN"):
                SSEEventFactory.create_event("UNKNOWN", {"test": "data"})

        finally:
            SSEEventFactory.EVENT_MAP = original_map

    def test_event_map_immutable(self):
        """Test that the EVENT_MAP is not accidentally modified."""
        original_length = len(SSEEventFactory.EVENT_MAP)
        original_keys = set(SSEEventFactory.EVENT_MAP.keys())

        # Try to create events
        SSEEventFactory.create_event("event", {"test": "data"})

        # Verify the map hasn't changed
        assert len(SSEEventFactory.EVENT_MAP) == original_length
        assert set(SSEEventFactory.EVENT_MAP.keys()) == original_keys

    def test_create_event_preserves_data_integrity(self):
        """Test that event creation preserves data integrity."""
        original_data = {"key": "value", "number": 42, "list": [1, 2, 3]}
        event = SSEEventFactory.create_event("event", original_data)

        # Check that data is preserved exactly
        assert event.data == original_data
        assert event.data["key"] == "value"
        assert event.data["number"] == 42
        assert event.data["list"] == [1, 2, 3]

        # Check that it's the same object (shallow copy)
        assert event.data is original_data

    def test_create_event_with_none_data(self):
        """Test creating an event with None data."""
        event = SSEEventFactory.create_event("event", None)
        assert event.event == "event"
        assert event.data is None

    def test_create_event_with_empty_string_event(self):
        """Test creating an event with empty string event type should raise error."""
        with pytest.raises(ValueError, match="Unknown event type: "):
            SSEEventFactory.create_event("", {"data": "test"})

    def test_event_map_contains_expected_types(self):
        """Test that the EVENT_MAP contains expected event types."""
        expected_types = {"event", "suspicion_detected", "clear", "warning", "info", "error", "multi_test", "test_event"}
        assert expected_types.issubset(set(SSEEventFactory.EVENT_MAP.keys()))
        assert len(SSEEventFactory.EVENT_MAP) >= len(expected_types)

        # Check that all mapped classes are subclasses of SSEEvent
        from core.services.sse.events.events import SSEEvent
        for event_class in SSEEventFactory.EVENT_MAP.values():
            assert issubclass(event_class, SSEEvent)

    @pytest.mark.parametrize("event_type,data", [
        ("event", {"simple": "data"}),
        ("suspicion_detected", {"confidence": 0.8, "details": "Test suspicion"}),
        ("clear", {"status": "cleared"}),
        ("warning", {"message": "Warning message"}),
        ("info", {"info": "Info message"}),
        ("error", {"error": "Error message"}),
        ("multi_test", {"id": 1, "message": "Multi test"}),
        ("test_event", {"id": 1, "data": "Test event"}),
        ("event", {"complex": {"nested": "value"}}),
        ("event", {"list": [1, 2, 3]}),
        ("event", {"empty": {}}),
    ])
    def test_create_event_parameterized(self, event_type, data):
        """Test creating events with various data types using parameterization."""
        event = SSEEventFactory.create_event(event_type, data)

        assert event.event == event_type
        assert event.data == data
        assert hasattr(event, 'validate_event')
        assert callable(getattr(event, 'validate_event'))

    def test_event_factory_singleton_behavior(self):
        """Test that event factory behaves consistently across multiple calls."""
        data1 = {"test": "data1"}
        data2 = {"test": "data2"}

        event1 = SSEEventFactory.create_event("event", data1)
        event2 = SSEEventFactory.create_event("event", data2)

        # Both should be valid events
        assert event1.event == "event"
        assert event2.event == "event"

        # But with different data
        assert event1.data == data1
        assert event2.data == data2

        # Should be different instances
        assert event1 is not event2
