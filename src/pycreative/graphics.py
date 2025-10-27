"""Public `pycreative.graphics` shims.

This module exposes a small, well-documented shim surface for graphics-related
helpers. Keep implementations tiny and delegate to the current Engine via the
SimpleSketchAPI when possible (to reuse engine plumbing and normalized
behaviour used by class-based sketches).
"""
from __future__ import annotations

from typing import Any

# Import the package-level helper to obtain the current engine instance.
from . import _get_engine


def blend_mode(mode: str) -> None:
    """Set the global blend mode used for subsequent drawing calls.

    This function delegates to the current engine's SimpleSketchAPI so the
    behaviour matches `this.blend_mode()` used inside class-based sketches.
    """
    eng = _get_engine()
    try:
        # Defer to the engine-provided SimpleSketchAPI if available.
        try:
            from core.engine.api.simple import SimpleSketchAPI
            return SimpleSketchAPI(eng).blend_mode(mode)
        except Exception:
            # Fallback: persist on engine object so replayers and presenters
            # can inspect the chosen blend mode.
            try:
                eng.blend_mode = str(mode)
            except Exception:
                pass
    except Exception:
        pass
    return None
