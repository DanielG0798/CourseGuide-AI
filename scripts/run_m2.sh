#!/usr/bin/env bash
# Run the Milestone 2 agent prototype with example inputs.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run: python -m venv .venv"
    exit 1
fi

source .venv/bin/activate

python -m src.m2.agent \
    --course physics_101 \
    --question "What is the difference between velocity and speed?"
