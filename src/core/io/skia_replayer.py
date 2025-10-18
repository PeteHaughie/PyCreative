"""Skia-based replayer: render recorded GraphicsBuffer commands into a
Skia CPU surface and write a PNG. This provides an authoritative Skia
snapshot for headless debugging when skia-python is available.
"""
    # mypy: ignore-errors
from __future__ import annotations

from typing import Any


def replay_to_image_skia(engine: Any, path: str) -> None:
    try:
        import skia
    except Exception:
        raise

    w = int(getattr(engine, 'width', 200))
    h = int(getattr(engine, 'height', 200))
    surf = skia.Surface(w, h)
    c = surf.getCanvas()

    # Default background
    try:
        c.clear(skia.Color4f(1.0, 1.0, 1.0, 1.0))
    except Exception:
        try:
            c.clear(0xFFFFFFFF)
        except Exception:
            pass

    # Delegate to the centralized replayer which understands all ops
    try:
        from core.io.replay_to_skia import replay_to_skia_canvas
        replay_to_skia_canvas(getattr(engine.graphics, 'commands', []), c)
    except Exception:
        # Fall back to previous conservative behaviour: nothing else to do
        pass

    img = surf.makeImageSnapshot()
    data = img.encodeToData()
    if data is None:
        raise RuntimeError('skia encodeToData returned None')

    # convert to bytes robustly
    b = None
    if hasattr(data, 'toBytes'):
        try:
            b = data.toBytes()
        except Exception:
            b = None
    if b is None and hasattr(data, 'asBytes'):
        try:
            b = data.asBytes()
        except Exception:
            b = None
    if b is None:
        try:
            b = bytes(data)
        except Exception:
            b = None
    if b is None:
        raise RuntimeError('Could not extract PNG bytes from skia.Data')

    with open(path, 'wb') as f:
        f.write(b)
