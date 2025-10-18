"""Adapters package for platform-specific backends.

Adapters should provide `register_api(engine)` or similar shims and avoid
heavy imports at module import time.
"""
from __future__ import annotations

# Re-export adapter submodules so callers can import from `core.adapters`.
# Keep this file intentionally thin; implementations live in sibling modules.
from . import pyglet_keyboard
from . import pyglet_mouse
from . import skia_gl_present

__all__ = [
	"pyglet_keyboard",
	"pyglet_mouse",
	"skia_gl_present",
]
