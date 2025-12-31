#!/bin/bash
# Start backend with Datadog LLM Observability

cd "$(dirname "$0")"

# Load environment variables from .env (properly handling values with spaces/special chars)
set -a
source .env
set +a

# Start with ddtrace
./venv/bin/ddtrace-run ./venv/bin/python app.py

