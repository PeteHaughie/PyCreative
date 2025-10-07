#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
pip install -e '.[test]'
pip install --upgrade ruff mypy

echo "Running ruff..."
ruff check . --extend-exclude examples --extend-exclude sketches

echo "Running mypy..."
mypy --config-file pyproject.toml

echo "Running tests..."
pytest -q
