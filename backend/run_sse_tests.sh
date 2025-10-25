#!/bin/bash

# SSE Tests Runner Script
# This script provides easy commands to run different types of SSE tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo_info "SSE Tests Runner"
echo_info "================"

# Check if we're in the right directory
if [[ ! -d "app/tests" ]]; then
    echo_error "Please run this script from the backend directory"
    exit 1
fi

# Check if dependencies are installed
echo_info "Checking dependencies..."
python -c "import pytest, pytest_asyncio, httpx" 2>/dev/null || {
    echo_warn "Installing test dependencies..."
    pip install -r ../requirements.txt
}

# Function to run tests
run_tests() {
    local test_pattern=$1
    local marker=$2
    local description=$3

    echo_info "Running $description..."

    if [[ -n "$marker" ]]; then
        pytest $test_pattern -m "$marker" -v
    else
        pytest $test_pattern -v
    fi
}

# Main menu
case "${1:-all}" in
    "all")
        echo_info "Running all SSE tests..."
        run_tests "app/tests/core/services/sse/" "" "all SSE unit tests"
        run_tests "app/tests/core/use_cases/test_sse_connection.py" "" "SSE use case tests"
        run_tests "app/tests/core/services/sse/test_sse_integration.py" "integration" "SSE integration tests"
        ;;
    "unit")
        echo_info "Running SSE unit tests..."
        run_tests "app/tests/core/services/sse/" "unit" "SSE unit tests"
        run_tests "app/tests/core/use_cases/test_sse_connection.py" "unit" "use case unit tests"
        ;;
    "integration")
        echo_info "Running SSE integration tests..."
        run_tests "app/tests/core/services/sse/test_sse_integration.py" "integration" "system integration tests"
        ;;
    "service")
        echo_info "Running SSE service tests..."
        run_tests "app/tests/core/services/sse/test_server_side_events.py" "" "service tests"
        run_tests "app/tests/core/services/sse/test_event_factory.py" "" "event factory tests"
        run_tests "app/tests/core/services/sse/test_sse_event.py" "" "event class tests"
        ;;
    "fast")
        echo_info "Running tests without integration (fast mode)..."
        run_tests "app/tests/core/services/sse/" "unit" "SSE unit tests"
        run_tests "app/tests/core/use_cases/test_sse_connection.py" "unit" "use case unit tests"
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  all         Run all SSE tests (default)"
        echo "  unit        Run unit tests only"
        echo "  integration Run integration tests only"
        echo "  service     Run service layer tests only"
        echo "  api         Run API layer tests only"
        echo "  coverage    Run tests with coverage report"
        echo "  fast        Run unit tests only (fastest)"
        echo "  help        Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 unit     # Run only unit tests"
        echo "  $0 coverage # Run tests with coverage"
        echo "  $0 api      # Test API endpoints only"
        exit 0
        ;;
    *)
        echo_error "Unknown command: $1"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac

echo_info "Tests completed!"
