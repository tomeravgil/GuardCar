import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from core.services.sse.server_side_events import ServerSideEventsService
from core.services.sse.events.event_factory import SSEEventFactory


class TestServerSideEventsService:
    """Test cases for the ServerSideEventsService class."""

    def test_service_initialization(self, shutdown_event):
        """Test service initialization with shutdown event."""
        service = ServerSideEventsService(shutdown_event)

        assert service.shutdown_event is shutdown_event
        assert isinstance(service.sse_queue, asyncio.Queue)

    def test_send_event_creates_and_queues_event(self, sse_service, sample_event_data):
        """Test that send_event creates an event and adds it to the queue."""
        # Mock the queue to verify put_nowait is called
        with patch.object(sse_service.sse_queue, 'put_nowait') as mock_put:
            sse_service.send_event("event", sample_event_data)

            # Verify the queue put was called
            mock_put.assert_called_once()

            # Get the event that was queued
            queued_event = mock_put.call_args[0][0]

            # Verify it's the correct event type and data
            assert queued_event.event == "event"
            assert queued_event.data == sample_event_data

    def test_send_event_multiple_events(self, sse_service):
        """Test sending multiple events in sequence."""
        with patch.object(sse_service.sse_queue, 'put_nowait') as mock_put:
            events_data = [
                {"id": 1, "message": "first"},
                {"id": 2, "message": "second"},
                {"id": 3, "message": "third"}
            ]

            for i, data in enumerate(events_data):
                sse_service.send_event("test_event", data)
                print(mock_put.call_count)
                # Verify each call
                assert mock_put.call_count == i + 1
                queued_event = mock_put.call_args[0][0]
                assert queued_event.event == "test_event"
                assert queued_event.data == data

    @pytest.mark.asyncio
    async def test_stream_events_exception_handling(self, sse_service):
        """Test exception handling in stream_events."""
        # Mock the queue to raise an exception
        with patch.object(sse_service.sse_queue, 'get', side_effect=Exception("Queue error")):
            stream_gen = sse_service.stream_events()

            # Set shutdown to stop the stream
            sse_service.shutdown_event.set()

            # Should handle the exception gracefully
            events = []
            try:
                async for event in stream_gen:
                    events.append(event)
            except Exception:
                pass  # Expected

            # Stream should have stopped
            assert len(events) == 0

    def test_service_reuse(self, shutdown_event):
        """Test that the service can be reused for multiple operations."""
        service = ServerSideEventsService(shutdown_event)

        # Should be able to send multiple events
        with patch.object(service.sse_queue, 'put_nowait') as mock_put:
            service.send_event("suspicion_detected", {"test": 1})
            service.send_event("warning", {"test": 2})
            service.send_event("info", {"test": 3})

            # Verify that put_nowait was called for each event
            assert mock_put.call_count == 3

            # Verify the events that were queued
            calls = mock_put.call_args_list
            for i, call in enumerate(calls):
                queued_event = call[0][0]
                assert hasattr(queued_event, 'to_sse_format')
                assert queued_event.event in ["suspicion_detected", "warning", "info"]
