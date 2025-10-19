"""Window and cursor helpers for the environment API.

These functions try to interact with a real window when available. In
headless runs they fall back to recording the intent on engine.graphics.
"""
from __future__ import annotations

from typing import Any, Optional


def fullscreen(engine: Any, display: Optional[int] = None):
    """Toggle fullscreen. In headless mode, record the request."""
    win = getattr(engine, '_window', None)
    if win is None:
        try:
            engine.graphics.record('fullscreen', display=display)
        except Exception:
            pass
        return
    try:
        if display is None:
            win.set_fullscreen(True)
        else:
            win.set_fullscreen(True)
    except Exception:
        pass


def cursor(engine: Any, *args, **kwargs):
    """Set or clear cursor. Minimal implementation: record the call."""
    try:
        engine.graphics.record('cursor', args=args, kwargs=kwargs)
    except Exception:
        pass


def no_cursor(engine: Any):
    try:
        engine.graphics.record('no_cursor')
    except Exception:
        pass


def window_move(engine: Any, x: int, y: int):
    try:
        engine.graphics.record('window_move', x=x, y=y)
    except Exception:
        pass


def window_moved(engine: Any):
    # lifecycle hook — no-op here; sketches implement this callback
    return None


def window_ratio(engine: Any, wide: int, high: int):
    try:
        engine.graphics.record('window_ratio', wide=wide, high=high)
    except Exception:
        pass


def window_resizeable(engine: Any, resizable: bool):
    win = getattr(engine, '_window', None)
    if win is None:
        try:
            engine.graphics.record('window_resizeable', resizable=bool(resizable))
        except Exception:
            pass
        return
    try:
        win.set_resizable(bool(resizable))
    except Exception:
        pass


def window_resized(engine: Any):
    # lifecycle hook — called by windowing system when resized. No-op.
    return None


def window_title(engine: Any, title: str):
    win = getattr(engine, '_window', None)
    if win is None:
        try:
            engine.graphics.record('window_title', title=title)
        except Exception:
            pass
        return
    try:
        win.set_caption(str(title))
    except Exception:
        pass
