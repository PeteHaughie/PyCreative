"""Engine-level snapshot orchestration.

This module provides a thin vended helper that mirrors the previous
Engine._save_frame behaviour but centralises engine-specific logging and
best-effort fallbacks. It prefers a custom `engine.snapshot_backend`, then
falls back to `core.io.snapshot.save_frame` which handles Pillow/no-op.
"""
from __future__ import annotations

import os
from typing import Any, Optional, Callable


def save_frame(engine: Any, path: str) -> None:
    """Save a frame for `engine` to `path`.

    Behaviour:
    - If `engine.snapshot_backend` exists, call it and record the backend
      used on the engine's graphics buffer.
    - Optionally prefer a Skia replayer for windowed engines (or when
      PYCREATIVE_USE_SKIA_REPLAYER=1) to capture on-screen rendering.
    - Otherwise delegate to `core.io.snapshot.save_frame` which will try
      Pillow and fall back to recording the request.
    """
    # 1) If engine provides a custom backend, prefer it
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
                # Allow fallback to the builtin writers
                pass
    except Exception:
        pass

    # 2) Attempt to import the pillow-based writer
    _save: Optional[Callable[[str, Any], None]] = None
    try:
        from core.io.snapshot import save_frame as _save
    except Exception:
        _save = None

    # 3) Decide whether to use Skia replayer (prefer for non-headless engines)
    use_skia = False
    try:
        if not getattr(engine, 'headless', True):
            use_skia = True
        elif os.getenv('PYCREATIVE_USE_SKIA_REPLAYER', '') == '1':
            use_skia = True
    except Exception:
        use_skia = False

    if use_skia:
        try:
            from core.io.skia_replayer import replay_to_image_skia

            # Build combined commands list: setup commands + current graphics
            try:
                setup_cmds = list(getattr(engine, '_setup_commands', []) or [])
            except Exception:
                setup_cmds = []
            try:
                current_cmds = list(getattr(engine.graphics, 'commands', []) or [])
            except Exception:
                current_cmds = []

            combined = setup_cmds + current_cmds

            # Ensure an opaque background is present for the replayer
            try:
                has_bg = any((c.get('op') == 'background') for c in combined)
            except Exception:
                has_bg = False
            if not has_bg:
                try:
                    sbg = getattr(engine, '_setup_background', None)
                    if sbg is not None:
                        bg_cmd = {'op': 'background', 'args': {'r': int(sbg[0]), 'g': int(sbg[1]), 'b': int(sbg[2])}, 'meta': {'seq': 0}}
                        combined = [bg_cmd] + combined
                    elif getattr(engine, '_setup_done', False):
                        bg_cmd = {'op': 'background', 'args': {'r': 200, 'g': 200, 'b': 200}, 'meta': {'seq': 0}}
                        combined = [bg_cmd] + combined
                except Exception:
                    pass

            # Create a minimal temp engine shape expected by the replayer
            try:
                import types

                temp_engine = types.SimpleNamespace()
                temp_engine.width = getattr(engine, 'width', 200)
                temp_engine.height = getattr(engine, 'height', 200)
                temp_engine.graphics = types.SimpleNamespace()
                temp_engine.graphics.commands = combined
            except Exception:
                temp_engine = engine

            replay_to_image_skia(temp_engine, path)
            try:
                engine.graphics.record('save_frame', path=path, backend='skia')
            except Exception:
                pass
            return
        except Exception:
            # Fall through to pillow/no-op writer
            pass

    # 4) Fallback to pillow-based writer if available
    if _save is not None:
        try:
            _save(path, engine)
            return
        except Exception:
            try:
                engine.graphics.record('save_frame', path=path, backend='none')
            except Exception:
                pass
            return

    # 5) Last resort: just record the request (no file written)
    try:
        engine.graphics.record('save_frame', path=path, backend='none')
    except Exception:
        pass
