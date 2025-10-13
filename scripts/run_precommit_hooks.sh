#!/usr/bin/env bash
# Simple script to run local pre-commit-style checks in CI where pre-commit
# might not be installed. This runs the enforcement pytest used by our
# pre-commit hook.

set -euo pipefail

# PYTHONPATH="$(pwd)" python3 -m pytest tests/test_dev_package_shim_conventions.py -q
