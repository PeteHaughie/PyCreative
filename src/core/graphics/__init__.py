"""Core graphics helpers and lightweight headless recording buffer.

Keep this package thin: implementations live in sibling modules.
"""
from __future__ import annotations

# Re-export submodules
from . import buffer

__all__ = [
    'buffer',
    'GraphicsBuffer',
    'PCGraphics',
    'create_graphics',
]

# Convenience re-export of the main class
from .buffer import GraphicsBuffer

# Expose PCGraphics implementation and create_graphics factory
from .pcgraphics import PCGraphics


def create_graphics(w: int, h: int):
    """Factory for creating PCGraphics surfaces.

    Returns a new PCGraphics(width, height). The function intentionally
    does not accept an engine parameter; PCGraphics will attempt to
    discover the current engine via `pycreative._get_engine()` when
    needed so callers may simply use `create_graphics(w, h)`.
    """
    return PCGraphics(int(w), int(h))
