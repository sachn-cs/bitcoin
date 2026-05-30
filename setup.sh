#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing package in development mode..."
pip install --upgrade pip
pip install -e .

echo "Installing test and development dependencies..."
pip install pytest pytest-cov pytest-benchmark hypothesis mypy ruff

echo "Running tests..."
python -m pytest tests/

echo "Done."
