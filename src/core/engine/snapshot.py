"""Engine-level snapshot orchestration.

This module provides a thin vended helper that mirrors the previous
Engine._save_frame behaviour but centralises engine-specific logging and
best-effort fallbacks. It prefers a custom `engine.snapshot_backend`, then
falls back to `core.io.snapshot.save_frame` which handles Pillow/no-op.
"""
from __future__ import annotations

from typing import Any


def save_frame(engine: Any, path: str) -> None:
    """Save a frame for `engine` to `path`.

    Behaviour:
    - If `engine.snapshot_backend` exists, call it and record the backend
      used on the engine's graphics buffer.
    - Otherwise delegate to `core.io.snapshot.save_frame` which will try
      Pillow and fall back to recording the request.
    """
    # Prefer engine-provided backend
    try:
        backend = getattr(engine, 'snapshot_backend', None)
        if backend is not None:
            try:
                backend(path, engine.width, engine.height, engine)
                try:
                    engine.graphics.record('save_frame', path=path, backend='custom')
                except Exception:
                    pass
                return
            except Exception:
                # Fall through to core.io snapshot writer
                pass
    except Exception:
        pass

    try:
        from core.io.snapshot import save_frame as _save
        # core.io.snapshot.save_frame will itself record which backend it
        # used (pillow/none). Call it and return.
        try:
            _save(path, engine)
        except Exception:
            try:
                engine.graphics.record('save_frame', path=path, backend='none')
            except Exception:
                pass
    except Exception:
        # As last resort, just record the request on the engine's buffer
        try:
            engine.graphics.record('save_frame', path=path, backend='none')
        except Exception:
            pass
