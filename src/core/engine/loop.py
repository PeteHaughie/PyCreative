"""Windowed loop and event-handler wiring helpers extracted from Engine.start.

This module registers pyglet window event handlers (on_draw, input
events) and schedules the update callback. It is implemented as
best-effort: imports are lazy and non-fatal so headless/test runs remain
import-safe.
"""
from __future__ import annotations

from typing import Any, Optional


def setup_window_loop(engine: Any, presenter: Any, max_frames: Optional[int] = None) -> None:
    """Register handlers on `engine._window`, schedule updates, and run the app.

    This mirrors the behaviour previously implemented in
    `Engine.start()`. The function is robust to adapter/module import
    failures and attempts to preserve the original semantics.
    """
    try:
        from core.engine.presenter import render_and_present
    except Exception:
        def render_and_present(p, cmds, fn):
            try:
                if callable(fn):
                    fn(cmds)
            except Exception:
                pass

    try:
        import pyglet
    except Exception:  # pragma: no cover - platform specific
        raise RuntimeError('pyglet is required for windowed mode')

    # Capture replay function if presenter exposes one
    replay_fn = getattr(presenter, 'replay_fn', None)

    # on_draw event
    @engine._window.event
    def on_draw():
        cmds = list(engine.graphics.commands)
        setup_bg = getattr(engine, '_setup_background', None)
        _setup_bg_local = setup_bg
        if _setup_bg_local is not None and not getattr(engine, '_setup_bg_applied', False):
            if not any(c.get('op') == 'background' for c in cmds):
                cmds = [{'op': 'background', 'args': {'r': int(_setup_bg_local[0]), 'g': int(_setup_bg_local[1]), 'b': int(_setup_bg_local[2])}, 'meta': {'seq': 0}}] + cmds
                engine._setup_bg_applied = True
        elif setup_bg is None and getattr(engine, '_setup_done', False):
            if not any(c.get('op') == 'background' for c in cmds) and not getattr(engine, '_default_bg_applied', False):
                cmds = [{'op': 'background', 'args': {'r': 200, 'g': 200, 'b': 200}, 'meta': {'seq': 0}}] + cmds
                engine._default_bg_applied = True

        # Best-effort GL clear to avoid flicker
        try:
            from pyglet import gl
            try:
                setup_bg = getattr(engine, '_setup_background', None)
                if setup_bg is not None:
                    r, g, b = float(setup_bg[0]) / 255.0, float(setup_bg[1]) / 255.0, float(setup_bg[2]) / 255.0
                    gl.glClearColor(r, g, b, 1.0)
                    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                elif getattr(engine, '_default_bg_applied', False):
                    gl.glClearColor(200.0 / 255.0, 200.0 / 255.0, 200.0 / 255.0, 1.0)
                    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            except Exception:
                pass
        except Exception:
            pass

        try:
            render_and_present(presenter, cmds, replay_fn)
        except Exception:
            # swallow non-fatal present errors to match previous behaviour
            pass

    # Helper to get normalize_button from adapters if available
    def _get_normalize_button():
        try:
            from core.adapters.pyglet_mouse import normalize_button as _nb
            return _nb
        except Exception:
            def _fallback(b: object) -> Optional[str]:
                try:
                    return str(b)
                except Exception:
                    return None
            return _fallback

    # Input handlers
    try:
        @engine._window.event
        def on_mouse_motion(x, y, dx, dy):
            try:
                hy = int(getattr(engine, 'height', 0))
                engine._apply_mouse_update(x, hy - int(y))
            except Exception:
                engine._apply_mouse_update(x, y)
            moved = getattr(engine.sketch, 'mouse_moved', None)
            if callable(moved):
                try:
                    try:
                        moved()
                    except TypeError:
                        this = __import__('core.engine.api.simple', fromlist=['SimpleSketchAPI']).SimpleSketchAPI(engine)
                        engine._call_sketch_method(moved, this)
                except Exception:
                    if getattr(engine, '_debug_handler_exceptions', False):
                        raise

        normalize_button = _get_normalize_button()

        @engine._window.event
        def on_mouse_press(x, y, button, modifiers):
            try:
                hy = int(getattr(engine, 'height', 0))
                engine._apply_mouse_update(x, hy - int(y))
            except Exception:
                engine._apply_mouse_update(x, y)
            try:
                engine.mouse_pressed = True
            except Exception:
                pass
            try:
                btn = normalize_button(button)
                if btn is not None:
                    engine.mouse_button = btn
            except Exception:
                pass
            handler = getattr(engine.sketch, 'mouse_pressed', None)
            if callable(handler):
                try:
                    try:
                        handler()
                    except TypeError:
                        this = __import__('core.engine.api.simple', fromlist=['SimpleSketchAPI']).SimpleSketchAPI(engine)
                        engine._call_sketch_method(handler, this)
                except Exception:
                    if getattr(engine, '_debug_handler_exceptions', False):
                        raise

        @engine._window.event
        def on_mouse_release(x, y, button, modifiers):
            try:
                hy = int(getattr(engine, 'height', 0))
                engine._apply_mouse_update(x, hy - int(y))
            except Exception:
                engine._apply_mouse_update(x, y)
            try:
                engine.mouse_pressed = False
            except Exception:
                pass
            try:
                btn = normalize_button(button)
                if btn is not None:
                    engine.mouse_button = btn
            except Exception:
                pass
            released = getattr(engine.sketch, 'mouse_released', None)
            if callable(released):
                try:
                    try:
                        released()
                    except TypeError:
                        this = __import__('core.engine.api.simple', fromlist=['SimpleSketchAPI']).SimpleSketchAPI(engine)
                        engine._call_sketch_method(released, this)
                except Exception:
                    if getattr(engine, '_debug_handler_exceptions', False):
                        raise
            clicked = getattr(engine.sketch, 'mouse_clicked', None)
            if callable(clicked):
                try:
                    try:
                        clicked()
                    except TypeError:
                        this = __import__('core.engine.api.simple', fromlist=['SimpleSketchAPI']).SimpleSketchAPI(engine)
                        engine._call_sketch_method(clicked, this)
                except Exception:
                    if getattr(engine, '_debug_handler_exceptions', False):
                        raise

        @engine._window.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            try:
                hy = int(getattr(engine, 'height', 0))
                engine._apply_mouse_update(x, hy - int(y))
            except Exception:
                engine._apply_mouse_update(x, y)
            try:
                engine.mouse_pressed = True
            except Exception:
                pass
            dragged = getattr(engine.sketch, 'mouse_dragged', None)
            if callable(dragged):
                try:
                    try:
                        dragged()
                    except TypeError:
                        this = __import__('core.engine.api.simple', fromlist=['SimpleSketchAPI']).SimpleSketchAPI(engine)
                        engine._call_sketch_method(dragged, this)
                except Exception:
                    if getattr(engine, '_debug_handler_exceptions', False):
                        raise

        @engine._window.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            handler = getattr(engine.sketch, 'mouse_wheel', None)
            if callable(handler):
                try:
                    class _Wheel:
                        def __init__(self, c):
                            self._c = c
                        def get_count(self):
                            return int(self._c)
                    try:
                        handler(_Wheel(scroll_y))
                    except TypeError:
                        this = __import__('core.engine.api.simple', fromlist=['SimpleSketchAPI']).SimpleSketchAPI(engine)
                        engine._call_sketch_method(handler, this)
                except Exception:
                    if getattr(engine, '_debug_handler_exceptions', False):
                        raise

        @engine._window.event
        def on_key_press(symbol, modifiers):
            try:
                try:
                    from core.adapters.pyglet_keyboard import normalize_event as _normalize
                except Exception:
                    def _normalize(event: Any) -> dict:
                        return {}
                ev = _normalize({'symbol': symbol, 'modifiers': modifiers})
                try:
                    engine.key = ev.get('key', None)
                except Exception:
                    pass
                try:
                    engine.key_code = ev.get('key_code', None)
                except Exception:
                    pass
                try:
                    engine.key_pressed = True
                except Exception:
                    pass
            except Exception:
                pass

            handler = getattr(engine.sketch, 'key_pressed', None)
            if callable(handler):
                try:
                    try:
                        handler()
                    except TypeError:
                        try:
                            handler(ev)
                        except TypeError:
                            this = __import__('core.engine.api.simple', fromlist=['SimpleSketchAPI']).SimpleSketchAPI(engine)
                            engine._call_sketch_method(handler, this)
                except Exception:
                    if getattr(engine, '_debug_handler_exceptions', False):
                        raise

        @engine._window.event
        def on_key_release(symbol, modifiers):
            try:
                try:
                    from core.adapters.pyglet_keyboard import normalize_event as _normalize
                except Exception:
                    def _normalize(event: Any) -> dict:
                        return {}
                ev = _normalize({'symbol': symbol, 'modifiers': modifiers})
                try:
                    engine.key = ev.get('key', None)
                except Exception:
                    pass
                try:
                    engine.key_code = ev.get('key_code', None)
                except Exception:
                    pass
                try:
                    engine.key_pressed = False
                except Exception:
                    pass
            except Exception:
                pass
            handler = getattr(engine.sketch, 'key_released', None)
            if callable(handler):
                try:
                    try:
                        handler()
                    except TypeError:
                        try:
                            handler(ev)
                        except TypeError:
                            this = __import__('core.engine.api.simple', fromlist=['SimpleSketchAPI']).SimpleSketchAPI(engine)
                            engine._call_sketch_method(handler, this)
                except Exception:
                    if getattr(engine, '_debug_handler_exceptions', False):
                        raise
    except Exception:
        # Best-effort only
        pass

    # whether start() was given an explicit max_frames
    engine._ignore_no_loop = False if max_frames is None else True

    def update(dt):
        if not engine._ignore_no_loop and not engine.looping and getattr(engine, '_no_loop_drawn', False):
            return
        engine.step_frame()
        if getattr(engine, '_verbose', False):
            for cmd in engine.graphics.commands:
                try:
                    print('VERBOSE CMD:', cmd)
                except Exception:
                    pass
        try:
            engine._window.invalid = True
        except Exception:
            pass
        if engine._frames_left is not None:
            engine._frames_left -= 1
            if engine._frames_left <= 0:
                try:
                    engine._window.close()
                except Exception:
                    pass
                import pyglet
                pyglet.app.exit()

    # schedule updates
    interval = None if engine.frame_rate < 1 else 1.0 / float(engine.frame_rate)
    if interval is None:
        pyglet.clock.schedule(update)
    else:
        pyglet.clock.schedule_interval(update, interval)

    # run app (suppress noisy stderr)
    try:
        devnull = open(__import__('os').devnull, 'w')
        from contextlib import redirect_stderr
        with redirect_stderr(devnull):
            pyglet.app.run()
    finally:
        try:
            devnull.close()
        except Exception:
            pass
