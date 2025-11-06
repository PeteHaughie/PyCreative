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
    # Try the Skia-backed implementation first (best-effort). If the
    # import or construction fails, fall back to the plain Python
    # `PCGraphics` implementation which uses Pillow/recording.
    try:
        from .pcgraphics_skia import PCGraphicsSkia

        try:
            # Create a Skia-backed PCGraphics but prefer the CPU Skia
            # surface in headless/test environments to avoid attempting
            # a GL context (which can hang). This keeps behavior Skia-
            # first while remaining safe in CI/headless runs.
            return PCGraphicsSkia(int(w), int(h), force_cpu=True)
        except Exception:
            # If construction fails, continue to fallback
            pass
    except Exception:
        # pcgraphics_skia not available — fall back silently
        pass

    return PCGraphics(int(w), int(h))
