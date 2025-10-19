"""Thin package shim for core.engine.api.

Keep implementation in `simple.py` so the package is easy to split later.
"""
from .simple import SimpleSketchAPI  # noqa: F401

__all__ = ["SimpleSketchAPI"]
