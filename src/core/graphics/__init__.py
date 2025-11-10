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

    Prefer a Skia-backed PCGraphics when the optional GPU-backed
    implementation is available. This keeps the library GPU-first and
    avoids falling back to Pillow-based rasterization for common cases.

    Returns a new PCGraphics(width, height) (Skia-backed when possible).
    """
    # Return the Skia-backed PCGraphics implementation as the canonical
    # offscreen surface. If Skia is unavailable the import will raise and
    # callers must handle that (the project is Skia-first by design).
    return PCGraphics(int(w), int(h))
