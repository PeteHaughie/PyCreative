"""Public shim for the core.engine package.

This package exposes the Engine class implemented in `impl.py` so
callers can import `core.engine.Engine`.
"""

from .impl import Engine

__all__ = ["Engine"]
