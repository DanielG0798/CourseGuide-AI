#!/usr/bin/env bash
# Run the Milestone 2 test suite.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run: python -m venv .venv"
    exit 1
fi

source .venv/bin/activate

pytest tests/m2 -v "$@"
