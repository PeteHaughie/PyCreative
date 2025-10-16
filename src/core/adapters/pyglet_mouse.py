"""Lightweight adapter to normalize pyglet mouse events to the engine's
internal event shape.

This module lazy-imports pyglet so tests and headless runs don't require
pyglet to be installed. It exposes small helpers that convert pyglet's
button constants and event objects into plain dicts the Engine can accept.
"""
from typing import Any, Dict, Optional


def _load_pyglet():
    try:
        import pyglet
        return pyglet
    except Exception:
        return None


def normalize_button(py_button: Any) -> Optional[str]:
    """Map pyglet mouse button constants to our string names.

    Returns 'LEFT', 'RIGHT', 'CENTER' or None if unknown or pyglet not
    available.
    """
    pyglet = _load_pyglet()
    if pyglet is None:
        # No pyglet available; we don't enforce a dependency in headless tests
        return None
    try:
        from pyglet.window import mouse as _m
        if py_button == getattr(_m, 'LEFT', None):
            return 'LEFT'
        if py_button == getattr(_m, 'RIGHT', None):
            return 'RIGHT'
        if py_button == getattr(_m, 'MIDDLE', None) or py_button == getattr(_m, 'MIDDLE_BUTTON', None):
            return 'CENTER'
    except Exception:
        pass
    return None


def normalize_event(event: Any) -> Dict[str, Any]:
    """Return a minimal dict with keys x, y, button (optional) and
    get_count (callable for wheel events if present).

    Accepts either a pyglet event-like object or a dict already shaped.
    """
    if event is None:
        return {}
    # If it's already a mapping, return a shallow copy
    try:
        if isinstance(event, dict):
            return dict(event)
    except Exception:
        pass

    out = {}
    # Duck-type commonly used attributes
    try:
        out['x'] = int(getattr(event, 'x', getattr(event, 'sx', None))) if getattr(event, 'x', None) is not None else None
    except Exception:
        out['x'] = None
    try:
        out['y'] = int(getattr(event, 'y', getattr(event, 'sy', None))) if getattr(event, 'y', None) is not None else None
    except Exception:
        out['y'] = None
    try:
        btn = getattr(event, 'button', None)
        if btn is not None:
            norm = normalize_button(btn)
            out['button'] = norm if norm is not None else btn
    except Exception:
        pass
    # For wheel events provide a get_count callable if possible
    try:
        if hasattr(event, 'get_count') and callable(getattr(event, 'get_count')):
            out['get_count'] = event.get_count
    except Exception:
        pass

    return out
