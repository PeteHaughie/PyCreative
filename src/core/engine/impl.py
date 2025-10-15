"""Minimal headless Engine implementation for tests and development.

This implementation focuses on headless execution: it records drawing
commands to an in-memory buffer (`graphics.commands`) so tests can assert
behaviour without opening windows or touching GPU libraries.

Not a production implementation — replace with real Engine when ready.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from core.graphics import GraphicsBuffer
from core.color import hsb_to_rgb
from .api_registry import APIRegistry

from core.adapters.skia_gl_present import SkiaGLPresenter
import os
from contextlib import redirect_stderr


class Engine:
    """A tiny headless engine for testing sketches.

    Lifecycle behaviour implemented:
    - call `setup(this)` once before the first draw
    - call `draw(this)` each frame depending on loop/no_loop/redraw
    - expose minimal helpers: size, no_loop, loop, redraw, save_frame
    """

    def __init__(self, sketch_module: Optional[Any] = None, headless: bool = True, present_mode: Optional[str] = None, force_gles: bool = False):
        self._no_loop_drawn = False
        self.sketch = sketch_module
        self.headless = headless
        self.api = APIRegistry()
        self.graphics = GraphicsBuffer()

        # lifecycle & environment
        self._setup_done = False
        self.looping = True
        self._redraw_requested = False
        # default frame rate (60 fps). A value of -1 means unrestricted.
        self.frame_rate = 60
        self.frame_count = 0
        # default size (can be overridden by sketch.size())
        # per API contract: default window is 200x200 when size() not called
        self.width = 200
        self.height = 200
        # default background color: rgb(200)
        self.background_color = (200, 200, 200)
        # drawing state
        # None means no fill/stroke; colors are (r,g,b) tuples
        self.fill_color: Optional[tuple] = (255, 255, 255)
        self.stroke_color: Optional[tuple] = (0, 0, 0)
        self.stroke_weight: int = 1
        # color mode: 'RGB' or 'HSB' (case-insensitive). Default RGB.
        self.color_mode = 'RGB'
        # pluggable snapshot backend: callable(path, width, height, engine)
        # default is None (the engine will attempt a Pillow-based write)
        self.snapshot_backend: Optional[Callable[[str, int, int, "Engine"], None]] = None

        # Normalize sketch: if a module contains a `Sketch` class, instantiate it
        self._normalize_sketch()

        self._running = False
        # store desired presenter mode if provided (None | 'vbo' | 'blit' | 'immediate')
        self.present_mode = present_mode
        # optional force GLES flag (for testing on platforms with GLES support)
        self.force_gles = bool(force_gles)

        # Register default API functions so SimpleSketchAPI delegates work
        try:
            from core.shape import rect as _rect, line as _line, point as _point
            # Register shape drawing functions that already record into
            # engine.graphics via core.shape.
            self.api.register('rect', lambda *a, **k: _rect(self, *a, **k))
            self.api.register('line', lambda *a, **k: _line(self, *a, **k))
            self.api.register('point', lambda *a, **k: _point(self, *a, **k))
            # circle helper is optional; register if present
            try:
                from core.shape import circle as _circle
                self.api.register('circle', lambda *a, **k: _circle(self, *a, **k))
            except Exception:
                pass
        except Exception:
            # If shape module isn't available, skip registration silently
            pass

        # Register math/random APIs if available (moved to core.random)
        try:
            from core.random import random as _rand, random_seed as _rand_seed, random_gaussian as _rand_gauss
            try:
                self.api.register('random', lambda *a, **k: _rand(self, *a, **k))
                self.api.register('random_seed', lambda *a, **k: _rand_seed(self, *a, **k))
                try:
                    self.api.register('random_gaussian', lambda *a, **k: _rand_gauss(self, *a, **k))
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            pass

        # Register simple color/stroke ops to record state changes as commands
        def _rec_fill(rgba):
            # store engine state and record a 'fill' op
            self.fill_color = tuple(int(x) for x in rgba)
            return self.graphics.record('fill', color=self.fill_color)

        def _rec_stroke(rgba):
            self.stroke_color = tuple(int(x) for x in rgba)
            return self.graphics.record('stroke', color=self.stroke_color)

        def _rec_no_fill():
            self.fill_color = None
            try:
                return self.graphics.record('no_fill')
            except Exception:
                return None

        def _rec_no_stroke():
            self.stroke_color = None
            try:
                return self.graphics.record('no_stroke')
            except Exception:
                return None

        def _rec_stroke_weight(w):
            self.stroke_weight = int(w)
            return self.graphics.record('stroke_weight', weight=int(w))

        try:
            self.api.register('fill', _rec_fill)
            self.api.register('stroke', _rec_stroke)
            self.api.register('stroke_weight', _rec_stroke_weight)
            # register no_fill/no_stroke so sketches can disable fills/strokes
            try:
                self.api.register('no_fill', lambda *a, **k: _rec_no_fill())
                self.api.register('no_stroke', lambda *a, **k: _rec_no_stroke())
            except Exception:
                pass
        except Exception:
            pass


    def register_api(self, registrant: Callable[["Engine"], None]):
        """Call a module's register_api(engine) hook to wire API functions.

        Accepts either a callable that will be invoked with the Engine, or
        a module-like object with a `register_api` attribute.
        """
        # Prefer module-like objects that expose `register_api` to avoid
        # treating classes (which are callable) as functions.
        if hasattr(registrant, 'register_api'):
            registrant.register_api(self)
            return
        if callable(registrant):
            # registrant is a function that accepts engine
            registrant(self)
            return
        raise TypeError('registrant must be callable or have register_api')

    def _normalize_sketch(self):
        """If the provided sketch is a module that defines a Sketch class,
        instantiate it so we always operate on an object with methods.
        """
        s = self.sketch
        if s is None:
            return
        # module with Sketch class
        if hasattr(s, 'Sketch') and isinstance(getattr(s, 'Sketch'), type):
            try:
                inst = s.Sketch()
                # Expose the engine on the instance so dynamic properties
                # (e.g., width/height) can access it without depending on
                # how API callables were attached.
                try:
                    setattr(inst, '_engine', self)
                except Exception:
                    pass
                # Attach a SimpleSketchAPI facade onto the instance so class-based
                # sketches can call self.size(), self.background(), etc.
                api = SimpleSketchAPI(self)
                # If this is a class-based sketch instance, create a tiny
                # dynamic subclass that exposes `width` and `height` as
                # properties delegating to the engine. This allows sketch
                # authors to use `self.width` inside class-based sketches.
                try:
                    cls = inst.__class__
                    if not hasattr(cls, 'width') and not hasattr(cls, 'height'):
                        def _make_width_prop():
                            return property(lambda self_obj: int(getattr(self_obj._engine, 'width', 0)))

                        def _make_height_prop():
                            return property(lambda self_obj: int(getattr(self_obj._engine, 'height', 0)))

                        Dynamic = type(f"{cls.__name__}_WithEnv", (cls,), {
                            'width': _make_width_prop(),
                            'height': _make_height_prop(),
                        })
                        try:
                            inst.__class__ = Dynamic
                        except Exception:
                            # If assignment fails for some types, silently continue
                            pass
                except Exception:
                    pass
                # Load the canonical binding list from the engine bindings
                # module. Fall back to an inline list if the import fails so
                # early boot or tests without the module still work.
                try:
                    from core.engine.bindings import SKETCH_CONVENIENCE_METHODS
                except Exception:
                    SKETCH_CONVENIENCE_METHODS = (
                        'size', 'background', 'window_title', 'no_loop', 'loop', 'redraw', 'save_frame',
                        'rect', 'line', 'circle', 'square', 'frame_rate',
                        'fill', 'stroke', 'stroke_weight',
                    )

                for name in SKETCH_CONVENIENCE_METHODS:
                    if hasattr(inst, name):
                        continue
                    # Prefer the API-provided implementation when available
                    fn = None
                    try:
                        fn = getattr(api, name)
                    except Exception:
                        fn = None

                    if fn is not None:
                        try:
                            setattr(inst, name, fn)
                            continue
                        except Exception:
                            # fall through to attempt a fallback
                            pass

                    # Provide tiny, well-scoped fallbacks for essential
                    # helpers so sketches remain usable even if the API
                    # registration or bindings import failed.
                    try:
                        if name == 'size':
                            setattr(inst, 'size', lambda w, h: inst._engine._set_size(int(w), int(h)))
                            continue
                        if name == 'background':
                            def _fb_background(*args, **kwargs):
                                # Try to delegate to core.color if available;
                                # otherwise record a background op with parsed RGB.
                                try:
                                    from core.color.background import set_background
                                    return set_background(inst._engine, *args, **kwargs)
                                except Exception:
                                    try:
                                        # Expect either a single grayscale, or r,g,b
                                        if len(args) == 1:
                                            v = int(args[0])
                                            inst._engine.graphics.record('background', r=v, g=v, b=v)
                                        else:
                                            r = int(args[0]); g = int(args[1]); b = int(args[2])
                                            inst._engine.graphics.record('background', r=r, g=g, b=b)
                                    except Exception:
                                        # Best-effort only
                                        pass
                            setattr(inst, 'background', _fb_background)
                            continue
                        if name == 'constrain':
                            def _fb_constrain(v, low, high):
                                try:
                                    v_f = float(v)
                                    low_f = float(low)
                                    high_f = float(high)
                                    return max(min(v_f, high_f), low_f)
                                except Exception:
                                    return v
                            setattr(inst, 'constrain', _fb_constrain)
                            continue
                        if name == 'random':
                            def _fb_random(*a, **k):
                                try:
                                    from core.random import random as _rand
                                    return _rand(inst._engine, *a)
                                except Exception:
                                    # Last resort: use Python's global random
                                    import random as _r
                                    if len(a) == 0:
                                        return _r.random()
                                    if len(a) == 1:
                                        return _r.random() * float(a[0])
                                    if len(a) == 2:
                                        return float(a[0]) + _r.random() * (float(a[1]) - float(a[0]))
                                    raise TypeError('random() expects 0,1 or 2 args')
                            setattr(inst, 'random', _fb_random)
                            continue
                        if name == 'random_seed':
                            def _fb_random_seed(s):
                                try:
                                    from core.random import random_seed as _rs
                                    return _rs(inst._engine, s)
                                except Exception:
                                    try:
                                        import random as _r
                                        _r.seed(int(s))
                                    except Exception:
                                        pass
                            setattr(inst, 'random_seed', _fb_random_seed)
                            continue
                    except Exception:
                        # If all fallback attempts fail, silently continue; the
                        # absence of the method is preferable to raising
                        # during sketch instantiation.
                        pass
                self.sketch = inst
            except Exception:
                # fall back to leaving as-is
                pass
        # Note: do NOT auto-instantiate bare classes passed as the sketch
        # module. Tests and examples sometimes pass a class with a free
        # function-style `draw(this)` defined; instantiating would change the
        # call signature (bound method receives `self`). Leave class as-is.

    def step_frame(self):
        """Execute a single frame: call sketch.setup()/draw() and record commands."""
        # Preserve setup commands (e.g., background) for every frame
        if not hasattr(self, '_setup_commands'):
            self._setup_commands = []
        # On first frame, record setup commands
        if not self._setup_done:
            self.graphics.clear()
            this = SimpleSketchAPI(self)
            setup = getattr(self.sketch, 'setup', None)
            if callable(setup):
                self._call_sketch_method(setup, this)
            # Capture and remove any background command emitted in setup so
            # it can be applied once only. Store its RGB for the presenter.
            recorded = list(self.graphics.commands)
            setup_bg = None
            remaining = []
            for cmd in recorded:
                if cmd.get('op') == 'background' and setup_bg is None:
                    # capture the first background command from setup
                    args = cmd.get('args', {})
                    setup_bg = (int(args.get('r', 200)), int(args.get('g', 200)), int(args.get('b', 200)))
                else:
                    remaining.append(cmd)
            # store the background captured during setup (or None)
            self._setup_background = setup_bg
            # store setup commands without background so they don't replay each frame
            self._setup_commands = remaining
            self._setup_done = True
            import logging as _logging
            try:
                _logging.getLogger(__name__).debug('Playing setup commands: %r', self._setup_commands)
            except Exception:
                pass
            try:
                _logging.getLogger(__name__).debug('step_frame: captured setup_background=%r', self._setup_background)
            except Exception:
                pass
        # If no_loop and already drawn, return immediately before any draw logic
        if not self.looping and getattr(self, '_no_loop_drawn', False):
            return
        else:
            self.graphics.clear()
            # Prepend setup commands to graphics.commands for each frame
            self.graphics.commands = list(self._setup_commands)
            # Headless: ensure the first recorded frame contains a background.
            # If the sketch provided a background in setup, that background was
            # captured to `_setup_background` and removed from setup commands to
            # avoid repeating in windowed mode. For headless runs we want the
            # recorded commands to include that background once so snapshots
            # and tests see an initialized canvas.
            if getattr(self, 'headless', False):
                if getattr(self, '_setup_background', None) is not None and not getattr(self, '_setup_bg_applied_headless', False):
                    bg = self._setup_background
                    # prepend a background command so it appears before other setup commands
                    self.graphics.commands.insert(0, {'op': 'background', 'args': {'r': int(bg[0]), 'g': int(bg[1]), 'b': int(bg[2])}, 'meta': {'seq': 0}})
                    self._setup_bg_applied_headless = True
                # Note: do not insert a default background automatically for headless
                # runs. Tests expect recorded command order to reflect only what the
                # sketch emitted. If a default background is desired for snapshots,
                # callers should emit one explicitly.

        # Note: do not auto-insert a default background here. If a sketch
        # wants a background it should call `this.background()` in setup()
        # or draw(). This keeps recorded command order intuitive for tests
        # and user code (drawn shapes appear in the same order they were
        # emitted).
        # Defer calling draw until we've decided whether this frame should run
        # (draw is invoked later once per frame). This avoids accidentally
        # calling draw twice during a single step (which previously caused
        # no_loop sketches to run draw() two times).
        # print("[DEBUG] Engine.step_frame() called. Sketch type:", type(self.sketch))
        # keep track of the sequence id before this frame so we can tag
        # newly-recorded commands with a frame number for debugging
        try:
            start_seq = int(getattr(self.graphics, '_seq', 0))
        except Exception:
            start_seq = 0
        if self.sketch is None:
            import logging as _logging
            try:
                _logging.getLogger(__name__).debug('No sketch attached to engine.')
            except Exception:
                pass
            return

        # (setup is run and recorded earlier in this method; do not run it again)

        # decide whether to run draw this frame
        # Semantics:
        # - If looping is enabled, draw every frame.
        # - If redraw() was requested, draw once.
        # - If no_loop() was called (looping==False) and no redraw() was
        #   requested, do NOT draw. This matches the expectations that
        #   calling no_loop() in setup() prevents any automatic draw.
        should_draw = False
        # If looping is enabled, draw every frame.
        if self.looping:
            should_draw = True
        # If redraw() requested, draw once.
        elif self._redraw_requested:
            should_draw = True
        # If the caller requested we ignore no_loop semantics (for example
        # the CLI --max-frames override), allow drawing even when looping
        # is disabled.
        elif not self.looping and getattr(self, '_ignore_no_loop', False):
            should_draw = True
        # If looping was disabled (no_loop called, e.g. in setup), allow a
        # single one-shot draw on the first frame and then stop. This matches
        # Processing semantics where calling no_loop() prevents continuous
        # looping but still allows one draw to run immediately after setup.
        elif not self.looping and not self._no_loop_drawn and self.frame_count == 0:
            should_draw = True

        if not should_draw:
            return

        # Only call draw once per frame
        this = SimpleSketchAPI(self)
        draw = getattr(self.sketch, 'draw', None)
        if callable(draw):
            self._call_sketch_method(draw, this)
        else:
            import logging as _logging
            try:
                _logging.getLogger(__name__).debug('draw is not callable.')
            except Exception:
                pass

        # Tag any commands recorded during this step with the current frame index
        try:
            for cmd in self.graphics.commands:
                meta = cmd.setdefault('meta', {})
                seq = int(meta.get('seq', 0))
                if seq > start_seq:
                    meta['frame'] = int(self.frame_count)
        except Exception:
            pass

        # reset one-shot redraw request
        if self._redraw_requested:
            self._redraw_requested = False

        # If looping is disabled and we are NOT ignoring no_loop, mark that
        # we've run the one-shot draw so subsequent frames are skipped early.
        if not self.looping and not getattr(self, '_ignore_no_loop', False):
            self._no_loop_drawn = True

        self.frame_count += 1

    def _call_sketch_method(self, fn: Callable, this: SimpleSketchAPI):
        """Call a sketch-provided function with either (this) or no args.

        Prefer calling with `this`; if the function raises a TypeError due to
        unexpected arguments, fall back to calling without arguments.
        """
        # If this is a bound method (has __self__), call without `this`.
        if hasattr(fn, '__self__') and getattr(fn, '__self__') is not None:
            return fn()

        # Otherwise, prefer calling with `this` (module-level functions expect it),
        # but fall back to no-arg call if that fails.
        try:
            return fn(this)
        except TypeError:
            return fn()

    def run_frames(self, n: int = 1, ignore_no_loop: bool = False):
        import time
        # Temporarily set a flag so step_frame can observe whether the
        # caller asked to ignore no_loop semantics for this run.
        prev_ignore = getattr(self, '_ignore_no_loop', False)
        self._ignore_no_loop = bool(ignore_no_loop)

        frame_counter = 0
        while frame_counter < n:
            # Stop if no_loop has already drawn, unless caller requested we
            # ignore no_loop semantics (for example, CLI --max-frames override).
            if not getattr(self, '_ignore_no_loop', False) and not self.looping and getattr(self, '_no_loop_drawn', False):
                break
            start = time.perf_counter()
            self.step_frame()
            # verbose output: print recorded commands after each frame
            if getattr(self, '_verbose', False):
                for cmd in self.graphics.commands:
                    try:
                        print('VERBOSE CMD:', cmd)
                    except Exception:
                        pass
            # enforce frame rate if requested and running in non-headless mode
            if self.frame_rate > 0 and not self.headless:
                elapsed = time.perf_counter() - start
                target = 1.0 / float(self.frame_rate)
                to_sleep = target - elapsed
                if to_sleep > 0:
                    time.sleep(to_sleep)
            frame_counter += 1
        # restore previous flag
        self._ignore_no_loop = prev_ignore

    # Windowed lifecycle helpers
    def start(self, max_frames: Optional[int] = None):
        """Start a windowed run of the sketch. If headless, behave like run_frames.

        When not headless, this creates a pyglet window and schedules frame
        updates at the chosen frame_rate. If max_frames is provided, the app
        will exit after that many frames.
        """
        if self.headless:
            # emulate windowed start in headless mode
            if max_frames is None:
                self.run_frames(1)
            else:
                # If caller provided max_frames, honor it even if the sketch
                # requests no_loop(). This mirrors the CLI semantics where
                # --max-frames should run the requested number of frames.
                self.run_frames(max_frames, ignore_no_loop=True)
            return

        # Lazy-import pyglet to avoid import-time dependency in tests
        try:
            import pyglet
            from pyglet import gl
            from pyglet import shapes
        except Exception as exc:  # pragma: no cover - platform specific
            raise RuntimeError('pyglet is required for windowed mode') from exc
        # Setup is now handled in step_frame; do not run it here

        # create window using potentially updated size from setup()
        # Ensure `setup()` runs at least once before creating the window so
        # that any setup-time background is captured. Pyglet may invoke
        # `on_draw` immediately after window creation which can race with
        # scheduled updates; running setup here avoids that race.
        if not getattr(self, '_setup_done', False):
            try:
                # Run setup and capture setup commands similar to step_frame()
                self.graphics.clear()
                this = SimpleSketchAPI(self)
                setup = getattr(self.sketch, 'setup', None)
                if callable(setup):
                    self._call_sketch_method(setup, this)
                recorded = list(self.graphics.commands)
                setup_bg = None
                remaining = []
                for cmd in recorded:
                    if cmd.get('op') == 'background' and setup_bg is None:
                        args = cmd.get('args', {})
                        setup_bg = (int(args.get('r', 200)), int(args.get('g', 200)), int(args.get('b', 200)))
                    else:
                        remaining.append(cmd)
                self._setup_background = setup_bg
                self._setup_commands = remaining
                self._setup_done = True
            except Exception:
                pass
        # Creating a pyglet window on macOS sometimes prints ObjC callback
        # exceptions during teardown even though the app continues to run.
        # Temporarily redirect stderr to hide that noise while still
        # propagating real failures.
        try:
            devnull = open(os.devnull, 'w')
            with redirect_stderr(devnull):
                self._window = pyglet.window.Window(
                    width=self.width, height=self.height, vsync=True)
        finally:
            try:
                devnull.close()
            except Exception:
                pass
        try:
            print(
                f'Engine: created window {self._window} size=({self.width},{self.height})')
        except Exception:
            pass
        # running until the user explicitly closes the window.
        self._frames_left = float(
            'inf') if max_frames is None else int(max_frames)

        # Create presenter once so the underlying FBO/texture and Skia surface
        # persist across frames. This allows drawings to accumulate if the
        # sketch does not clear the background each frame (Processing-style).
        presenter = SkiaGLPresenter(self.width, self.height, force_present_mode=self.present_mode, force_gles=self.force_gles)
        replay_fn = presenter.replay_fn

        @self._window.event
        def on_draw():
            try:
                import logging as _logging
                _logging.getLogger(__name__).debug("on_draw: _setup_done=%r, _setup_background=%r, _setup_bg_applied=%r, _default_bg_applied=%r",
                                                     getattr(self,'_setup_done',None), getattr(self,'_setup_background',None), getattr(self,'_setup_bg_applied',False), getattr(self,'_default_bg_applied',False))
            except Exception:
                pass
            # Build commands to replay. If setup provided a background, ensure
            # it's applied once by prepending it to the very first frame's
            # commands. The engine tracks `_setup_bg_applied` to avoid
            # reapplying the setup background on subsequent frames.
            cmds = list(self.graphics.commands)
            setup_bg = getattr(self, '_setup_background', None)
            if setup_bg is not None and not getattr(self, '_setup_bg_applied', False):
                # Only prepend if the current frame doesn't already specify a background
                if not any(c.get('op') == 'background' for c in cmds):
                    cmds = [{'op': 'background', 'args': {'r': int(setup_bg[0]), 'g': int(setup_bg[1]), 'b': int(setup_bg[2])}, 'meta': {'seq': 0}}] + cmds
                    # Mark that we've applied the setup background once so it
                    # doesn't clear subsequent frames.
                    self._setup_bg_applied = True
            # Only apply the engine default background if no setup background
            # exists at all. If the sketch provided a setup background we
            # should never inject the default gray background later.
            elif setup_bg is None and getattr(self, '_setup_done', False):
                # If the sketch did not set any background during setup and
                # we haven't applied a default background yet, apply a single
                # default rgb(200) background so the first frame starts with
                # a reasonable canvas instead of uninitialized pixels.
                if not any(c.get('op') == 'background' for c in cmds) and not getattr(self, '_default_bg_applied', False):
                    cmds = [{'op': 'background', 'args': {'r': 200, 'g': 200, 'b': 200}, 'meta': {'seq': 0}}] + cmds
                    self._default_bg_applied = True

            # If the sketch changed size during setup/draw, ensure presenter
            # backing textures match the new size.
            if presenter.width != int(self.width) or presenter.height != int(self.height):
                try:
                    presenter.resize(self.width, self.height)
                except Exception:
                    pass

            try:
                presenter.render_commands(cmds, replay_fn)
            except Exception as e:
                import logging as _logging
                try:
                    _logging.getLogger(__name__).debug('presenter.render_commands raised: %r', repr(e))
                except Exception:
                    pass
                # Fall through to present attempt; present may still show previous content
            # Clear the default framebuffer to the setup/default background
            # colour before presenting the presenter's texture. This avoids a
            # visible one-frame flicker where the window may briefly show a
            # different background (OS/window) before the texture is blitted.
            try:
                from pyglet import gl
                try:
                    setup_bg = getattr(self, '_setup_background', None)
                    if setup_bg is not None:
                        r, g, b = float(setup_bg[0]) / 255.0, float(setup_bg[1]) / 255.0, float(setup_bg[2]) / 255.0
                        gl.glClearColor(r, g, b, 1.0)
                        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                    elif getattr(self, '_default_bg_applied', False):
                        # If we've applied the engine default background, clear
                        # the window to that colour so the presented texture
                        # overlays a predictable base.
                        gl.glClearColor(200.0 / 255.0, 200.0 / 255.0, 200.0 / 255.0, 1.0)
                        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
                except Exception:
                    pass
            except Exception:
                pass

            try:
                presenter.present()
            except Exception:
                # Present failures are non-fatal; previous frame contents may
                # still be visible. Do not spam stdout in normal runs.
                pass
        
        # Note: we intentionally avoid creating a pyglet Image backed by
        # the presenter's GL texture. Wrapping an external GL texture in a
        # pyglet.image.Texture can cause GL_INVALID_OPERATION depending on
        # driver/context state. The presenter.present() implementation
        # performs the direct GL textured-quad draw and is the preferred
        # display path.

        # whether start() was given an explicit max_frames (in which case
        # we should ignore sketch no_loop semantics for the duration of this
        # run)
        self._ignore_no_loop = False if max_frames is None else True

        def update(dt):
            # Stop if no_loop has already drawn unless we're explicitly
            # ignoring no_loop for this run.
            if not self._ignore_no_loop and not self.looping and getattr(self, '_no_loop_drawn', False):
                return
            # print(f"[DEBUG] Engine.update() called. dt={dt}, frames_left={self._frames_left}")
            self.step_frame()
            # verbose: echo recorded commands to stdout for debugging
            if getattr(self, '_verbose', False):
                for cmd in self.graphics.commands:
                    try:
                        print('VERBOSE CMD:', cmd)
                    except Exception:
                        pass
            # request a redraw
            try:
                self._window.invalid = True
            except Exception:
                pass
            # decrement frame counter and exit when done
            if self._frames_left is not None:
                self._frames_left -= 1
                if self._frames_left <= 0:
                    try:
                        self._window.close()
                    except Exception:
                        pass
                    import pyglet
                    pyglet.app.exit()

        # schedule updates at frame_rate if set, otherwise use default clock tick
        interval = None if self.frame_rate < 1 else 1.0 / \
            float(self.frame_rate)
        if interval is None:
            pyglet.clock.schedule(update)
            try:
                print('Engine: scheduled update (unspecified interval)')
            except Exception:
                pass
        else:
            pyglet.clock.schedule_interval(update, interval)
            try:
                print(f'Engine: scheduled update interval={interval}s')
            except Exception:
                pass

        # run the app (blocks until exit). Suppress noisy stderr messages from
        # the platform/pyglet bridge while still allowing the app to run.
        try:
            print('Engine: entering pyglet.app.run()')
        except Exception:
            pass
        try:
            devnull = open(os.devnull, 'w')
            with redirect_stderr(devnull):
                pyglet.app.run()
        finally:
            try:
                devnull.close()
            except Exception:
                pass
        try:
            print('Engine: pyglet.app.run() returned')
        except Exception:
            pass

    def stop(self):
        """Stop a running window (if any)."""
        try:
            import pyglet
            pyglet.app.exit()
        except Exception:
            pass

    # Engine-side helpers used by SimpleSketchAPI
    def _set_size(self, w: int, h: int):
        """Set engine size and resize the window if one exists.

        This should be safe to call in headless mode (no-op for window). If a
        pyglet window exists, call its set_size method and update the GL
        viewport where possible so rendering matches the new size.
        """
        self.width = int(w)
        self.height = int(h)
        # If a window exists, resize it and try to update GL viewport.
        win = getattr(self, '_window', None)
        if win is not None:
            try:
                win.set_size(self.width, self.height)
            except Exception:
                # Some window implementations may not support set_size; ignore.
                pass
            # Attempt to update GL viewport if pyglet.gl is available
            try:
                from pyglet import gl
                gl.glViewport(0, 0, int(self.width), int(self.height))
            except Exception:
                pass

    def _no_loop(self):
        self.looping = False

    def _loop(self):
        self.looping = True

    def _redraw(self):
        self._redraw_requested = True

    def _save_frame(self, path: str):
        """Save a placeholder snapshot for headless mode. If Pillow is
        available, write a simple PNG. Otherwise, record the request.
        """
        try:
            from core.io.snapshot import save_frame as _save
            return _save(path, self)
        except Exception:
            # As a very last resort, record the request without writing
            try:
                self.graphics.record('save_frame', path=path, backend='none')
            except Exception:
                pass

from .api import SimpleSketchAPI
