"""Environment settings helpers (size, frame control, pixel density, etc.).

These functions accept an Engine instance as the first argument and
manipulate or read engine state. Kept small to avoid import-time cycles.
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
