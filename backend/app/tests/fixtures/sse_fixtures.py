import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi.testclient import TestClient

from core.services.sse.server_side_events import ServerSideEventsService
from core.services.sse.i_server_side_events_service import IServerSideEventsService
from core.use_cases.sse_connection import ServerSideEventsUseCase


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def shutdown_event():
    """Create a shutdown event for testing."""
    return asyncio.Event()


@pytest.fixture
def sse_service(shutdown_event):
    """Create a ServerSideEventsService instance for testing."""
    return ServerSideEventsService(shutdown_event)


@pytest.fixture
def mock_sse_service():
    """Create a mock SSE service for testing."""
    mock_service = Mock(spec=IServerSideEventsService)
    mock_service.send_event = Mock()
    mock_service.stream_events = AsyncMock()
    return mock_service


@pytest.fixture
def sse_use_case(mock_sse_service):
    """Create a ServerSideEventsUseCase with mock service."""
    return ServerSideEventsUseCase(sse_service=mock_sse_service)


@pytest.fixture
def sample_event_data():
    """Sample event data for testing."""
    return {
        "id": "test-123",
        "type": "suspicion_detected",
        "timestamp": "2024-01-01T12:00:00Z",
        "confidence": 0.85,
        "details": "Suspicious activity detected"
    }


@pytest.fixture
def sample_sse_event():
    """Sample SSE event for testing."""
    return {
        "event": "test_event",
        "data": {"message": "test message"}
    }
