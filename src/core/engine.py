"""Thin facade for the Engine implementation.

Keep the public surface tiny. Implementations live in
`src.core.engine.impl` (this file is a small shim that re-exports the
implementation class so callers import `core.engine.Engine` safely).
"""

from .engine_impl import Engine  # re-export the compact implementation

__all__ = ["Engine"]
