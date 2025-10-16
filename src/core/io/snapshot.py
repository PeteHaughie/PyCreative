"""Snapshot backends for saving frames and images.

Provides a small high-level API used by Engine to save frames. This module
tries registered/custom backends first, then falls back to a Pillow writer
or a no-op record when not available.
"""
from typing import Any


def save_frame(path: str, engine: Any) -> None:
    # prefer custom backend if provided
    if getattr(engine, 'snapshot_backend', None) is not None:
        try:
            engine.snapshot_backend(path, engine.width, engine.height, engine)
            engine.graphics.record('save_frame', path=path, backend='custom')
            return
        except Exception:
            pass

    # Pillow fallback
    try:
        from PIL import Image
        img = Image.new('RGBA', (engine.width, engine.height), (255, 255, 255, 255))
        img.save(path)
        engine.graphics.record('save_frame', path=path, backend='pillow')
        return
    except Exception:
        # fallback: just record the request (no file written)
        engine.graphics.record('save_frame', path=path, backend='none')
