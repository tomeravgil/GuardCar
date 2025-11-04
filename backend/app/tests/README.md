# SSE Tests

This directory contains comprehensive tests for the Server-Sent Events (SSE) functionality in the GuardCar2.0 backend.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Global test configuration and fixtures
├── core/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── sse/
│   │       ├── __init__.py
│   │       ├── test_sse_event.py        # Tests for SSEEvent class
│   │       ├── test_event_factory.py    # Tests for SSEEventFactory
│   │       ├── test_server_side_events.py  # Tests for ServerSideEventsService
│   │       └── test_sse_integration.py  # Integration tests
│   └── use_cases/
│       ├── __init__.py
│       └── test_sse_connection.py       # Tests for ServerSideEventsUseCase
├── api/
│   ├── __init__.py
│   └── routers/
│       ├── __init__.py
│       └── test_sse.py                  # Tests for SSE API endpoint
└── fixtures/
    ├── __init__.py
    └── sse_fixtures.py                  # Test fixtures and utilities
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Async tests only
pytest -m asyncio

# SSE tests only
pytest tests/core/services/sse/

# API tests only
pytest tests/api/routers/
```

### Run with coverage
```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# Generate coverage report for SSE only
pytest tests/core/services/sse/ --cov=app.core.services.sse --cov-report=html
```

### Run specific test files
```bash
# Test the service layer
pytest tests/core/services/sse/test_server_side_events.py

# Test the API layer
pytest tests/api/routers/test_sse.py

# Test integration
pytest tests/core/services/sse/test_sse_integration.py
```

## Test Coverage

### Unit Tests

#### SSEEvent Tests (`test_sse_event.py`)
- Event creation and initialization
- SSE format conversion (`to_sse_format()`)
- Event validation
- Special characters and edge cases
- Field immutability

#### SSEEventFactory Tests (`test_event_factory.py`)
- Event creation from factory
- Unknown event type handling
- Event map integrity
- Data preservation
- Parameterized testing

#### ServerSideEventsService Tests (`test_server_side_events.py`)
- Service initialization
- Event queuing (`send_event()`)
- Async streaming (`stream_events()`)
- Queue management
- Shutdown behavior
- Error handling
- Concurrent operations

#### ServerSideEventsUseCase Tests (`test_sse_connection.py`)
- Use case initialization
- StreamingResponse creation
- Service integration
- Error propagation
- Multiple execution

### Integration Tests

#### API Router Tests (`test_sse.py`)
- Endpoint accessibility
- HTTP method and path validation
- Response format and headers
- Dependency injection
- Error handling
- Concurrent requests

#### System Integration Tests (`test_sse_integration.py`)
- End-to-end event flow
- Async streaming integration
- Service lifecycle management
- Error propagation through layers
- Format compliance

## Test Fixtures

The `sse_fixtures.py` file provides reusable fixtures:

- `shutdown_event`: Asyncio event for graceful shutdown
- `sse_service`: ServerSideEventsService instance
- `mock_sse_service`: Mocked service for unit testing
- `sse_use_case`: Use case with mocked service
- `sample_event_data`: Sample event data for testing
- `sample_sse_event`: Sample SSE event structure

## Best Practices

### Async Testing
- Use `@pytest.mark.asyncio` for async test functions
- Use `async def` for async test methods
- Properly handle event loops in async tests

### Mocking
- Mock external dependencies appropriately
- Use `AsyncMock` for async methods
- Verify method calls and return values

### Integration Testing
- Test the complete flow from service to API
- Override FastAPI dependencies for testing
- Test error scenarios and edge cases

### Coverage
- Aim for >90% code coverage
- Exclude test files and abstract methods from coverage
- Use coverage reports to identify untested code paths

## Dependencies

Test dependencies are specified in `requirements.txt`:
- `pytest`: Core testing framework
- `pytest-asyncio`: Async testing support
- `httpx`: HTTP client for integration testing
- `pytest-mock`: Mocking utilities
- `pytest-cov`: Coverage reporting
