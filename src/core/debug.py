"""Lightweight debug helper used across the runtime.

Use the environment variable PYCREATIVE_DEBUG=1 to enable prints. This
keeps heavy logging out of tests unless explicitly requested.
"""
import os
import sys


def debug(msg: str) -> None:
    try:
        if os.environ.get('PYCREATIVE_DEBUG', '') == '1':
            print(f"[PyCreative DEBUG] {msg}", file=sys.stderr)
    except Exception:
        pass
