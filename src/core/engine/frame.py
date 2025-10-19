"""Frame-stepping helper extracted from Engine.step_frame.

This module provides a single function `step_frame(engine)` which executes a
single frame: runs setup once, decides whether to call update/draw for the
frame, records commands, tags them with the frame index, and advances
frame_count. It mirrors the behaviour previously implemented inline on
Engine to make the implementation easier to test and refactor.
"""
from __future__ import annotations

from typing import Any


def step_frame(engine: Any) -> None:
    """Execute a single frame for the given engine instance.

    This function intentionally performs only engine-local state changes and
    uses best-effort exception handling to match the previous semantics.
    """
    # Preserve setup commands (e.g., background) for every frame
    if not hasattr(engine, '_setup_commands'):
        engine._setup_commands = []
    # On first frame, record setup commands
    if not getattr(engine, '_setup_done', False):
        try:
            engine.graphics.clear()
        except Exception:
            pass
        this = __import__('core.engine.api.simple', fromlist=['SimpleSketchAPI']).SimpleSketchAPI(engine)
        setup = getattr(engine.sketch, 'setup', None)
        if callable(setup):
            try:
                engine._call_sketch_method(setup, this)
            except Exception:
                pass
        # Capture and remove any background command emitted in setup so
        # it can be applied once only. Store its RGB for the presenter.
        try:
            recorded = list(engine.graphics.commands)
        except Exception:
            recorded = []
        setup_bg = None
        remaining = []
        for cmd in recorded:
            try:
                if cmd.get('op') == 'background' and setup_bg is None:
                    args = cmd.get('args', {})
                    setup_bg = (int(args.get('r', 200)), int(args.get('g', 200)), int(args.get('b', 200)))
                else:
                    remaining.append(cmd)
            except Exception:
                try:
                    remaining.append(cmd)
                except Exception:
                    pass
        # store the background captured during setup (or None)
        try:
            engine._setup_background = setup_bg
        except Exception:
            pass
        # store setup commands without background so they don't replay each frame
        try:
            engine._setup_commands = remaining
        except Exception:
            pass
        try:
            engine._setup_done = True
        except Exception:
            pass
        try:
            import logging as _logging
            _logging.getLogger(__name__).debug('Playing setup commands: %r', engine._setup_commands)
        except Exception:
            pass
        try:
            import logging as _logging
            _logging.getLogger(__name__).debug('step_frame: captured setup_background=%r', getattr(engine, '_setup_background', None))
        except Exception:
            pass

    # If no_loop and already drawn, return immediately before any draw logic
    if not engine.looping and getattr(engine, '_no_loop_drawn', False):
        return
    else:
        try:
            engine.graphics.clear()
        except Exception:
            pass
        # Prepend setup commands to graphics.commands for each frame
        try:
            engine.graphics.commands = list(getattr(engine, '_setup_commands', []))
        except Exception:
            try:
                engine.graphics.commands = []
            except Exception:
                pass
        # Headless: ensure the first recorded frame contains a background.
        if getattr(engine, 'headless', False):
            _bg_local = getattr(engine, '_setup_background', None)
            if _bg_local is not None and not getattr(engine, '_setup_bg_applied_headless', False):
                bg = _bg_local
                try:
                    engine.graphics.commands.insert(0, {'op': 'background', 'args': {'r': int(bg[0]), 'g': int(bg[1]), 'b': int(bg[2])}, 'meta': {'seq': 0}})
                except Exception:
                    pass
                try:
                    engine._setup_bg_applied_headless = True
                except Exception:
                    pass

    # decide whether to run draw this frame
    should_draw = False
    if engine.looping:
        should_draw = True
    elif getattr(engine, '_redraw_requested', False):
        should_draw = True
    elif not engine.looping and getattr(engine, '_ignore_no_loop', False):
        should_draw = True
    elif not engine.looping and not getattr(engine, '_no_loop_drawn', False) and getattr(engine, 'frame_count', 0) == 0:
        should_draw = True

    if not should_draw:
        return

    # Only call update() then draw() once per frame.
    this = __import__('core.engine.api.simple', fromlist=['SimpleSketchAPI']).SimpleSketchAPI(engine)
    update_fn = getattr(engine.sketch, 'update', None)
    if callable(update_fn):
        try:
            engine._call_sketch_method(update_fn, this)
        except Exception:
            pass

    draw = getattr(engine.sketch, 'draw', None)
    if callable(draw):
        engine._call_sketch_method(draw, this)
    else:
        try:
            import logging as _logging
            _logging.getLogger(__name__).debug('draw is not callable.')
        except Exception:
            pass

    # Tag any commands recorded during this step with the current frame index
    try:
        start_seq = int(getattr(engine.graphics, '_seq', 0))
    except Exception:
        start_seq = 0
    try:
        for cmd in engine.graphics.commands:
            try:
                meta = cmd.setdefault('meta', {})
                seq = int(meta.get('seq', 0))
                if seq > start_seq:
                    meta['frame'] = int(engine.frame_count)
            except Exception:
                pass
    except Exception:
        pass

    # reset one-shot redraw request
    try:
        if getattr(engine, '_redraw_requested', False):
            engine._redraw_requested = False
    except Exception:
        pass

    # If looping is disabled and we are NOT ignoring no_loop, mark that
    # we've run the one-shot draw so subsequent frames are skipped early.
    try:
        if not engine.looping and not getattr(engine, '_ignore_no_loop', False):
            engine._no_loop_drawn = True
    except Exception:
        pass

    try:
        engine.frame_count += 1
    except Exception:
        try:
            engine.frame_count = int(getattr(engine, 'frame_count', 0)) + 1
        except Exception:
            pass
