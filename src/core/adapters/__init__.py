"""Adapters package for platform-specific backends.

Adapters should provide `register_api(engine)` or similar shims and avoid
heavy imports at module import time.
"""
from __future__ import annotations

__all__ = []
