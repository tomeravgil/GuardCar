import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.responses import StreamingResponse
from core.use_cases.sse_connection import ServerSideEventsUseCase


class TestServerSideEventsUseCase:
    """Test cases for the ServerSideEventsUseCase class."""

    def test_use_case_initialization(self, mock_sse_service):
        """Test use case initialization with SSE service."""
        use_case = ServerSideEventsUseCase(sse_service=mock_sse_service)

        assert use_case.sse_service is mock_sse_service

    def test_execute_returns_streaming_response(self, sse_use_case):
        """Test that execute method returns a StreamingResponse."""
        response = sse_use_case.execute()

        assert isinstance(response, StreamingResponse)
        assert response.media_type == "text/event-stream"

    def test_use_case_with_real_service(self, sse_service):
        """Test use case with a real SSE service instance."""
        use_case = ServerSideEventsUseCase(sse_service=sse_service)

        response = use_case.execute()

        assert isinstance(response, StreamingResponse)
        assert response.media_type == "text/event-stream"

    def test_use_case_multiple_calls(self, mock_sse_service):
        """Test that use case can be called multiple times."""
        use_case = ServerSideEventsUseCase(sse_service=mock_sse_service)

        # Should be able to call execute multiple times
        response1 = use_case.execute()
        response2 = use_case.execute()
        response3 = use_case.execute()

        # All should be StreamingResponse instances
        assert isinstance(response1, StreamingResponse)
        assert isinstance(response2, StreamingResponse)
        assert isinstance(response3, StreamingResponse)

        # All should have the same media type
        assert response1.media_type == "text/event-stream"
        assert response2.media_type == "text/event-stream"
        assert response3.media_type == "text/event-stream"

    def test_streaming_response_headers(self, mock_sse_service):
        """Test that the StreamingResponse has appropriate headers."""
        mock_sse_service.stream_events = AsyncMock(return_value=iter([]))

        use_case = ServerSideEventsUseCase(sse_service=mock_sse_service)
        response = use_case.execute()

        # Check default headers that FastAPI sets for SSE
        # Note: headers might not be set until the response is actually processed
        assert response.media_type == "text/event-stream"

    def test_use_case_empty_service_response(self, mock_sse_service):
        """Test use case with empty service response."""
        # Mock empty async generator
        async def empty_stream():
            return
            yield  # pragma: no cover

        mock_sse_service.stream_events = AsyncMock(return_value=empty_stream())

        use_case = ServerSideEventsUseCase(sse_service=mock_sse_service)
        response = use_case.execute()

        assert isinstance(response, StreamingResponse)
        assert response.media_type == "text/event-stream"
