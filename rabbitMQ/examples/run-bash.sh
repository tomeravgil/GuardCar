#!/usr/bin/env bash
# Usage: ./run-consumer.sh [python_file] 
# Default python file: consumer.py

set -euo pipefail

PYFILE="${1:-consumer.py}"

# Pick a python executable
if command -v python >/dev/null 2>&1; then
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "Python not found on PATH." >&2
  exit 1
fi

# Ensure pika is installed
if ! "$PY" - <<'PYCHK' >/dev/null 2>&1; then
import importlib.util as u
import sys
sys.exit(0 if u.find_spec("pika") else 1)
PYCHK
then
  echo "Installing pika..."
  "$PY" -m pip install --user pika==1.3.2
fi

# Set defaults only if not already set in the environment
: "${AMQP_HOST:=localhost}"
: "${AMQP_PORT:=5672}"
: "${AMQP_VHOST:=/}"
: "${AMQP_USER:=jack}"
: "${AMQP_PASS:=jack}"

# Run the consumer script
exec "$PY" "$PYFILE"