"""Engine-aware environment helpers.

Each function accepts an Engine instance as the first argument and
manipulates or reads engine state. These are intended to be registered
with the Engine API registry or used by SimpleSketchAPI wrappers.
"""
from __future__ import annotations

from typing import Any, Optional


def size(engine: Any, w: int, h: int) -> None:
    """Set the sketch size on the engine."""
    engine._set_size(int(w), int(h))


def settings(engine: Any):
    """Placeholder for settings() lifecycle hook. No-op at engine level.

    Sketch authors implement this function in their sketch; the engine
    will call it if present. Exposed here for completeness.
    """
    return None


def frame_count(engine: Any) -> int:
    return int(getattr(engine, 'frame_count', 0))


def frame_rate(engine: Any, fps: Optional[int] = None):
    """Get or set the engine frame rate.

    If fps is None, return the current frame_rate. Otherwise set it.
    """
    if fps is None:
        return getattr(engine, 'frame_rate', 60)
    try:
        engine.frame_rate = int(fps)
    except Exception:
        raise TypeError('frame_rate expects an integer')


def delay(engine: Any, ms: int) -> None:
    """Pause execution for ms milliseconds (blocking)."""
    import time

    time.sleep(float(ms) / 1000.0)


def display_width(engine: Any) -> int:
    # For simplicity, mirror engine.width (windowed runs may override)
    return int(getattr(engine, 'width', 0))


def display_height(engine: Any) -> int:
    return int(getattr(engine, 'height', 0))


def height(engine: Any) -> int:
    return int(getattr(engine, 'height', 0))


def width(engine: Any) -> int:
    return int(getattr(engine, 'width', 0))


def pixel_density(engine: Any, density: Optional[int] = None):
    """Get or set pixel density. Stores value on engine as `pixel_density`.

    This implementation is minimal: it records the value and updates
    convenience `pixel_width`/`pixel_height` attributes.
    """
    if density is None:
        return int(getattr(engine, 'pixel_density', 1))
    d = int(density)
    setattr(engine, 'pixel_density', d)
    # update pixel dimensions
    setattr(engine, 'pixel_width', int(getattr(engine, 'width', 0)) * d)
    setattr(engine, 'pixel_height', int(getattr(engine, 'height', 0)) * d)


def pixel_width(engine: Any) -> int:
    return int(getattr(engine, 'pixel_width', getattr(engine, 'width', 0)))


def pixel_height(engine: Any) -> int:
    return int(getattr(engine, 'pixel_height', getattr(engine, 'height', 0)))


def display_density(engine: Any) -> float:
    return float(getattr(engine, 'display_density', 1.0))


def focused(engine: Any) -> bool:
    return bool(getattr(engine, '_window_focused', True))


def fullscreen(engine: Any, display: Optional[int] = None):
    """Toggle fullscreen. In headless mode, record the request.

    When a real window exists, attempt to call its set_fullscreen method if
    available.
    """
    win = getattr(engine, '_window', None)
    if win is None:
        # record the intent for tests
        try:
            engine.graphics.record('fullscreen', display=display)
        except Exception:
            pass
        return
    try:
        if display is None:
            win.set_fullscreen(True)
        else:
            # try to set full screen on given display index where supported
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
