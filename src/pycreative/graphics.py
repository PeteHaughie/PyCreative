"""Thin public graphics shims re-exporting core graphics helpers.

These functions delegate to the current engine (set via
`pycreative.set_current_engine`) so tests and examples can use the
`pycreative.graphics` namespace without importing core internals.
"""
from __future__ import annotations


from . import _get_engine


def blend_mode(mode: str) -> None:
    eng = _get_engine()
    try:
        # Try to delegate to the SimpleSketchAPI for consistent behaviour
        from core.engine.api.simple import SimpleSketchAPI

        return SimpleSketchAPI(eng).blend_mode(mode)
    except Exception:
        # Fallback: persist on engine object so replayers and presenters
        # can inspect the chosen blend mode.
        try:
            setattr(eng, 'blend_mode', str(mode))
        except Exception:
            pass
    return None


__all__ = ['blend_mode']
