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
    # Filename template handling: replace runs of '#' in the basename with
    # a zero-padded representation of `engine.frame_count`. Also support an
    # empty/None path by using the Processing-style default "screen-0000.png".
    try:
        try:
            frame_val = int(getattr(engine, 'frame_count', 0))
        except Exception:
            frame_val = 0

        if not path:
            path = f"screen-{frame_val:04d}.png"
        else:
            # operate on the basename so directory components are preserved
            import re

            try:
                dirpart = os.path.dirname(path)
                base = os.path.basename(path)
                if base and ('#' in base):
                    def _rep(m):
                        w = len(m.group(0))
                        return f"{frame_val:0{w}d}"

                    new_base = re.sub(r"#+", _rep, base)
                    path = os.path.join(dirpart, new_base) if dirpart else new_base
            except Exception:
                # best-effort only; fall back to provided path
                pass

    except Exception:
        # non-fatal; continue with provided path
        pass

    # Normalize path: if a relative path was provided, and we can determine
    # the sketch's folder from the engine, resolve the path so files are
    # written into the sketch's directory by default (Processing behaviour).
    try:
        if not os.path.isabs(path):
            sketch_dir = None
            # Prefer the original sketch module the CLI passed (if present)
            try:
                smod = getattr(engine, '_sketch_module', None)
                if smod is not None:
                    sf = getattr(smod, '__file__', None)
                    if sf:
                        sketch_dir = os.path.dirname(os.path.abspath(sf))
            except Exception:
                sketch_dir = None

            # If CLI-provided sketch not available, fall back to normalized sketch
            if sketch_dir is None:
                try:
                    s = getattr(engine, 'sketch', None)
                    if s is not None:
                        sf = getattr(s, '__file__', None)
                        if sf:
                            sketch_dir = os.path.dirname(os.path.abspath(sf))
                        else:
                            try:
                                mod = getattr(s.__class__, '__module__', None)
                                if mod:
                                    import sys as _sys

                                    mod_obj = _sys.modules.get(mod)
                                    if mod_obj is not None:
                                        mf = getattr(mod_obj, '__file__', None)
                                        if mf:
                                            sketch_dir = os.path.dirname(os.path.abspath(mf))
                            except Exception:
                                pass
                except Exception:
                    sketch_dir = None

            if sketch_dir is None:
                # Fall back to current working directory
                sketch_dir = os.getcwd()

            # join and normalize
            try:
                path = os.path.abspath(os.path.join(sketch_dir, path))
            except Exception:
                path = os.path.abspath(path)

    except Exception:
        # best-effort only; continue with provided path on failure
        try:
            path = os.path.abspath(path)
        except Exception:
            pass

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

    # If this is a windowed engine and a presenter is available, decide
    # whether to snapshot immediately or defer to the presenter. If we are
    # currently inside draw(), defer by recording a save_frame op so the
    # presenter will write the file after it renders the commands. If we
    # are not in draw (for example, a key handler after a frame was
    # presented), snapshot the presenter's surface immediately.
    try:
        presenter = getattr(engine, '_presenter', None)
        # If a presenter exists (windowed run) prefer an immediate snapshot
        # when the call originates outside of `draw()`; otherwise defer by
        # recording a `save_frame` command so the presenter writes it after
        # rendering the current frame. This avoids lost queued requests when
        # the app isn't animating and the user saves from an input handler.
        if presenter is not None and not getattr(engine, 'headless', True):
            in_draw = bool(getattr(engine, '_in_draw', False))
            # If we're inside draw(), queue for the presenter to handle
            if in_draw:
                try:
                    pending = getattr(engine, '_pending_save_frames', None)
                    if pending is None:
                        pending = []
                        try:
                            setattr(engine, '_pending_save_frames', pending)
                        except Exception:
                            pass
                    pending.append({'op': 'save_frame', 'args': {'path': path}, 'meta': {'seq': 0}})
                except Exception:
                    pass
                return

            # Not in draw(): try to snapshot the presenter's current surface
            try:
                surf = None
                # Prefer the presenter's current Skia surface if available
                surf = getattr(presenter, 'surface', None)
                if surf is None:
                    # ask the presenter to create a fresh surface
                    try:
                        surf = presenter.create_skia_surface()
                    except Exception:
                        surf = None
                if surf is not None:
                    try:
                        img = None
                        try:
                            img = surf.makeImageSnapshot()
                        except Exception:
                            img = None
                        if img is not None:
                            data = None
                            try:
                                data = img.encodeToData()
                            except Exception:
                                data = None
                            b = None
                            if data is not None:
                                try:
                                    if hasattr(data, 'toBytes'):
                                        b = data.toBytes()
                                    elif hasattr(data, 'tobytes'):
                                        b = data.tobytes()
                                    else:
                                        b = bytes(data)
                                except Exception:
                                    b = None
                            if b:
                                try:
                                    with open(path, 'wb') as _f:
                                        _f.write(b)
                                    try:
                                        engine.graphics.record('save_frame', path=path, backend='presenter_immediate')
                                    except Exception:
                                        pass
                                    return
                                except Exception:
                                    # fall through to queueing below
                                    pass
                    except Exception:
                        pass
            except Exception:
                pass

            # If immediate snapshot failed, queue for presenter as a fallback
            try:
                pending = getattr(engine, '_pending_save_frames', None)
                if pending is None:
                    pending = []
                    try:
                        setattr(engine, '_pending_save_frames', pending)
                    except Exception:
                        pass
                pending.append({'op': 'save_frame', 'args': {'path': path}, 'meta': {'seq': 0}})
            except Exception:
                pass
            return
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

            # Note: Do not attempt to snapshot the presenter's surface here
            # synchronously — when `save_frame()` is invoked from inside
            # `draw()` the actual rendering hasn't been performed yet. The
            # presenter will handle any recorded 'save_frame' ops during its
            # `render_commands` call so the snapshot captures the just-rendered
            # pixels. Fall through to the replayer fallback.

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
