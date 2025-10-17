"""Minimal headless Engine implementation for tests and development.

This implementation focuses on headless execution: it records drawing
commands to an in-memory buffer (`graphics.commands`) so tests can assert
behaviour without opening windows or touching GPU libraries.

Not a production implementation — replace with real Engine when ready.
"""
from __future__ import annotations

from typing import Any, Callable, Optional
from core.graphics import GraphicsBuffer
from .api_registry import APIRegistry
from core.adapters.skia_gl_present import SkiaGLPresenter
from contextlib import redirect_stderr
import os
from .api import SimpleSketchAPI


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
        # Mouse/input state (defaults per docs)
        # mouse_x/y report current mouse coords (int); pmouse_x/y are previous
        self.mouse_x: int = 0
        self.mouse_y: int = 0
        self.pmouse_x: int = 0
        self.pmouse_y: int = 0
        # mouse_pressed boolean and mouse_button ('LEFT'|'RIGHT'|'CENTER'|None)
        self.mouse_pressed: bool = False
        self.mouse_button: Optional[str] = None
        # color mode: 'RGB' or 'HSB' (case-insensitive). Default RGB.
        self.color_mode = 'RGB'
        # pluggable snapshot backend: callable(path, width, height, engine)
        # default is None (the engine will attempt a Pillow-based write)
        self.snapshot_backend: Optional[Callable[[str, int, int, "Engine"], None]] = None

        # Normalize sketch: if a module contains a `Sketch` class, instantiate it
        self._normalize_sketch()

        # Debugging toggle: when True, exceptions raised by user handlers
        # will be re-raised instead of swallowed. Can be enabled via
        # environment variable PYCREATIVE_DEBUG_HANDLER_EXCEPTIONS.
        try:
            self._debug_handler_exceptions = bool(int(os.getenv('PYCREATIVE_DEBUG_HANDLER_EXCEPTIONS', '0')))
        except Exception:
            self._debug_handler_exceptions = False

        self._running = False
        # store desired presenter mode if provided (None | 'vbo' | 'blit' | 'immediate')
        self.present_mode = present_mode
        # optional force GLES flag (for testing on platforms with GLES support)
        self.force_gles = bool(force_gles)

        # Register default API functions so SimpleSketchAPI delegates work
        try:
            from core.engine.registrations import register_shape_apis, register_random_and_noise
            try:
                register_shape_apis(self)
            except Exception:
                pass
            try:
                register_random_and_noise(self)
            except Exception:
                pass
        except Exception:
            # best-effort only; continue if registrations can't be imported
            pass

        # Register simple color/stroke ops to record state changes as commands
        def _rec_fill(rgba):
            # store engine state and record a 'fill' op
            self.fill_color = tuple(int(x) for x in rgba)
            # also record any alpha that may be set on the engine
            return self.graphics.record('fill', color=self.fill_color, fill_alpha=getattr(self, 'fill_alpha', None))

        def _rec_stroke(rgba):
            self.stroke_color = tuple(int(x) for x in rgba)
            return self.graphics.record('stroke', color=self.stroke_color, stroke_alpha=getattr(self, 'stroke_alpha', None))

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

                        def _make_mouse_x_prop():
                            return property(lambda self_obj: int(getattr(self_obj._engine, 'mouse_x', 0)))

                        def _make_mouse_y_prop():
                            return property(lambda self_obj: int(getattr(self_obj._engine, 'mouse_y', 0)))

                        def _make_pmouse_x_prop():
                            return property(lambda self_obj: int(getattr(self_obj._engine, 'pmouse_x', 0)))

                        def _make_pmouse_y_prop():
                            return property(lambda self_obj: int(getattr(self_obj._engine, 'pmouse_y', 0)))

                        def _make_mouse_button_prop():
                            return property(lambda self_obj: getattr(self_obj._engine, 'mouse_button', None))

                        # Create a descriptor that exposes a read-only boolean
                        # view of engine.mouse_pressed while still allowing
                        # the user-defined `mouse_pressed()` handler to be
                        # invoked if the developer calls it as a function.
                        class _MousePressedProxy:
                            def __init__(self, handler=None):
                                # handler is the original unbound function from the user's class (may be None)
                                self._handler = handler

                            def __get__(self, instance, owner=None):
                                # Return a bound proxy object that is both bool-like
                                # and callable (if a handler exists).
                                if instance is None:
                                    return self

                                class _Bound:
                                    def __init__(self, inst, handler):
                                        self._inst = inst
                                        self._handler = handler

                                    def __bool__(self):
                                        try:
                                            return bool(getattr(self._inst._engine, 'mouse_pressed', False))
                                        except Exception:
                                            return False

                                    # allow int(self.mouse_pressed) or contexts that check truthiness
                                    def __int__(self):
                                        return 1 if bool(self) else 0

                                    def __call__(self, *a, **kw):
                                        # If user defined a handler, call it with the
                                        # instance as first arg (bound semantics).
                                        if callable(self._handler):
                                            try:
                                                return self._handler(self._inst, *a, **kw)
                                            except Exception:
                                                if getattr(self._inst._engine, '_debug_handler_exceptions', False):
                                                    raise
                                                return None
                                        # no handler defined: noop
                                        return None

                                    def __repr__(self):
                                        try:
                                            return f"<mouse_pressed proxy {bool(self)}>"
                                        except Exception:
                                            return "<mouse_pressed proxy>"

                                return _Bound(instance, self._handler)

                        # Capture the original unbound mouse_pressed function if present
                        orig_mouse_pressed = None
                        try:
                            m = getattr(cls, 'mouse_pressed', None)
                            if callable(m):
                                # store the unbound function so the proxy can call it
                                orig_mouse_pressed = m
                        except Exception:
                            orig_mouse_pressed = None

                        Dynamic = type(f"{cls.__name__}_WithEnv", (cls,), {
                            'width': _make_width_prop(),
                            'height': _make_height_prop(),
                            'mouse_x': _make_mouse_x_prop(),
                            'mouse_y': _make_mouse_y_prop(),
                            'pmouse_x': _make_pmouse_x_prop(),
                            'pmouse_y': _make_pmouse_y_prop(),
                            'mouse_button': _make_mouse_button_prop(),
                            'mouse_pressed': _MousePressedProxy(handler=orig_mouse_pressed),
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
                from typing import Sequence
                # Declare _sketch_methods once and assign in branches to avoid
                # static redefinition errors from type checkers.
                _sketch_methods: Sequence[str]
                try:
                    from core.engine.bindings import SKETCH_CONVENIENCE_METHODS
                    # Normalize to a sequence of strings so static checkers see a
                    # consistent type regardless of the concrete collection used
                    # in the bindings module.
                    _sketch_methods = list(SKETCH_CONVENIENCE_METHODS)
                except Exception:
                    _sketch_methods = [
                        'size', 'background', 'window_title', 'no_loop', 'loop', 'redraw', 'save_frame',
                        'rect', 'line', 'circle', 'square', 'frame_rate',
                        'fill', 'stroke', 'stroke_weight',
                    ]

                for name in _sketch_methods:
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
                                            r = int(args[0])
                                            g = int(args[1])
                                            b = int(args[2])
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
                        if name == 'map':
                            def _fb_map(value, start1, stop1, start2, stop2):
                                try:
                                    v = float(value)
                                    s1 = float(start1)
                                    s2 = float(stop1)
                                    t1 = float(start2)
                                    t2 = float(stop2)
                                    if s2 == s1:
                                        raise ValueError('map: start1 and stop1 cannot be equal')
                                    return t1 + (v - s1) * (t2 - t1) / (s2 - s1)
                                except Exception:
                                    return value
                            setattr(inst, 'map', _fb_map)
                            continue
                        if name == 'lerp':
                            def _fb_lerp(a, b, amt):
                                try:
                                    return (1.0 - float(amt)) * float(a) + float(amt) * float(b)
                                except Exception:
                                    return a
                            setattr(inst, 'lerp', _fb_lerp)
                            continue
                        if name == 'norm':
                            def _fb_norm(value, start, stop):
                                try:
                                    v = float(value)
                                    s = float(start)
                                    t = float(stop)
                                    if t == s:
                                        raise ValueError('norm: start and stop cannot be equal')
                                    return (v - s) / (t - s)
                                except Exception:
                                    return 0.0
                            setattr(inst, 'norm', _fb_norm)
                            continue
                        if name == 'round':
                            def _fb_round(v):
                                try:
                                    return round(float(v))
                                except Exception:
                                    try:
                                        return round(v)
                                    except Exception:
                                        return v
                            setattr(inst, 'round', _fb_round)
                            continue
                        if name == 'noise':
                            def _fb_noise(v, *rest):
                                # best-effort fallback: use Python's random for smooth-ish output
                                try:
                                    import random as _r
                                    # single-value noise: map random to [0,1]
                                    return float(_r.random())
                                except Exception:
                                    return 0.0
                            setattr(inst, 'noise', _fb_noise)
                            continue
                        if name == 'noise_seed':
                            def _fb_noise_seed(s):
                                try:
                                    import random as _r
                                    _r.seed(int(s))
                                except Exception:
                                    pass
                                return None
                            setattr(inst, 'noise_seed', _fb_noise_seed)
                            continue
                        if name == 'noise_detail':
                            def _fb_noise_detail(lod, falloff=0.5):
                                # noop fallback
                                return None
                            setattr(inst, 'noise_detail', _fb_noise_detail)
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
                _bg_local = getattr(self, '_setup_background', None)
                if _bg_local is not None and not getattr(self, '_setup_bg_applied_headless', False):
                    bg = _bg_local
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

        # Only call update() then draw() once per frame. update() runs before
        # draw() and can be used to change sketch state (movement, physics,
        # collisions) prior to rendering. Use _call_sketch_method so we
        # gracefully handle both bound methods and module-level functions.
        this = SimpleSketchAPI(self)
        # Call optional update() first
        update_fn = getattr(self.sketch, 'update', None)
        if callable(update_fn):
            try:
                self._call_sketch_method(update_fn, this)
            except Exception:
                # Do not let update errors stop the frame; continue to draw
                pass

        # Then call draw()
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
        # If fn is a bound method (has __self__ set) then it already
        # has the instance bound and should be called without passing
        # `this`. This avoids errors like "takes 1 positional argument
        # but 2 were given" when methods are bound.
        try:
            bound_self = getattr(fn, '__self__', None)
            if bound_self is not None:
                return fn()
        except Exception:
            pass

        # Prefer calling with `this`; if the callable doesn't accept an
        # argument (raises TypeError), fall back to calling without args.
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
                # Create window; cast to Any for static checking so mypy
                # does not attempt to verify pyglet's internal abstract base
                # classes here.
                from typing import cast, Any as _Any
                _win = pyglet.window.Window(width=self.width, height=self.height, vsync=True)  # type: ignore
                # cast to Any to avoid mypy attempting to validate pyglet's
                # abstract base classes in this context.
                self._window = cast(_Any, _win)
        finally:
            try:
                devnull.close()
            except Exception:
                pass
        # Apply any window title requested during setup()/before the window
        # existed. This ensures calls to this.window_title(...) in setup are
        # persisted and applied once the window is available.
        try:
            pending = getattr(self, '_pending_window_title', None)
            if pending is not None:
                try:
                    self._window.set_caption(str(pending))
                except Exception:
                    pass
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
        # Presenter may be a complex object from adapters; treat as Any to
        # avoid instantiating abstract types during static checking.
        from typing import Any as _Any
        presenter: _Any = SkiaGLPresenter(self.width, self.height, force_present_mode=self.present_mode, force_gles=self.force_gles)
        replay_fn = getattr(presenter, 'replay_fn', None)

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
            # mypy: setup_bg may be None or a tuple; assign to local and
            # check before indexing.
            _setup_bg_local = setup_bg
            if _setup_bg_local is not None and not getattr(self, '_setup_bg_applied', False):
                # Only prepend if the current frame doesn't already specify a background
                if not any(c.get('op') == 'background' for c in cmds):
                    cmds = [{'op': 'background', 'args': {'r': int(_setup_bg_local[0]), 'g': int(_setup_bg_local[1]), 'b': int(_setup_bg_local[2])}, 'meta': {'seq': 0}}] + cmds
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
        
        # Register input event handlers on the created window so real
        # pyglet-driven events update engine state and dispatch sketch
        # handlers. Import adapters lazily so headless tests remain import-safe.
        try:
            # Helper to obtain a normalize_button function from adapters if
            # available, otherwise provide a local fallback with a stable
            # signature for static type checkers.
            from typing import Optional as _Optional

            def _get_normalize_button():
                try:
                    from core.adapters.pyglet_mouse import normalize_button as _nb
                    return _nb
                except Exception:
                    def _fallback(b: object) -> _Optional[str]:
                        try:
                            return str(b)
                        except Exception:
                            return None
                    return _fallback

            @self._window.event
            def on_mouse_motion(x, y, dx, dy):
                try:
                    # Update engine mouse coords and call sketch handler
                    # Convert window coords (origin bottom-left) to sketch
                    # coords (origin top-left) by flipping the Y axis.
                    try:
                        hy = int(getattr(self, 'height', 0))
                        self._apply_mouse_update(x, hy - int(y))
                    except Exception:
                        self._apply_mouse_update(x, y)
                except Exception:
                    pass
                moved = getattr(self.sketch, 'mouse_moved', None)
                if callable(moved):
                    try:
                        try:
                            moved()
                        except TypeError:
                            this = SimpleSketchAPI(self)
                            self._call_sketch_method(moved, this)
                    except Exception:
                        # Swallow handler exceptions unless debug flag set
                        if getattr(self, '_debug_handler_exceptions', False):
                            raise

            @self._window.event
            def on_mouse_press(x, y, button, modifiers):
                normalize_button = _get_normalize_button()
                try:
                    try:
                        hy = int(getattr(self, 'height', 0))
                        self._apply_mouse_update(x, hy - int(y))
                    except Exception:
                        self._apply_mouse_update(x, y)
                except Exception:
                    pass
                try:
                    self.mouse_pressed = True
                except Exception:
                    pass
                try:
                    btn = normalize_button(button)
                    if btn is not None:
                        self.mouse_button = btn
                except Exception:
                    pass
                handler = getattr(self.sketch, 'mouse_pressed', None)
                if callable(handler):
                    try:
                        try:
                            handler()
                        except TypeError:
                            this = SimpleSketchAPI(self)
                            self._call_sketch_method(handler, this)
                    except Exception:
                        if getattr(self, '_debug_handler_exceptions', False):
                            raise

            @self._window.event
            def on_mouse_release(x, y, button, modifiers):
                normalize_button = _get_normalize_button()
                try:
                    try:
                        hy = int(getattr(self, 'height', 0))
                        self._apply_mouse_update(x, hy - int(y))
                    except Exception:
                        self._apply_mouse_update(x, y)
                except Exception:
                    pass
                try:
                    self.mouse_pressed = False
                except Exception:
                    pass
                try:
                    btn = normalize_button(button)
                    if btn is not None:
                        self.mouse_button = btn
                except Exception:
                    pass
                released = getattr(self.sketch, 'mouse_released', None)
                if callable(released):
                    try:
                        try:
                            released()
                        except TypeError:
                            this = SimpleSketchAPI(self)
                            self._call_sketch_method(released, this)
                    except Exception:
                        if getattr(self, '_debug_handler_exceptions', False):
                            raise
                clicked = getattr(self.sketch, 'mouse_clicked', None)
                if callable(clicked):
                    try:
                        try:
                            clicked()
                        except TypeError:
                            this = SimpleSketchAPI(self)
                            self._call_sketch_method(clicked, this)
                    except Exception:
                        if getattr(self, '_debug_handler_exceptions', False):
                            raise

            @self._window.event
            def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
                try:
                    try:
                        hy = int(getattr(self, 'height', 0))
                        self._apply_mouse_update(x, hy - int(y))
                    except Exception:
                        self._apply_mouse_update(x, y)
                except Exception:
                    pass
                try:
                    self.mouse_pressed = True
                except Exception:
                    pass
                dragged = getattr(self.sketch, 'mouse_dragged', None)
                if callable(dragged):
                    try:
                        try:
                            dragged()
                        except TypeError:
                            this = SimpleSketchAPI(self)
                            self._call_sketch_method(dragged, this)
                    except Exception:
                        if getattr(self, '_debug_handler_exceptions', False):
                            raise

            @self._window.event
            def on_mouse_scroll(x, y, scroll_x, scroll_y):
                # scroll_y is commonly used as the wheel count
                handler = getattr(self.sketch, 'mouse_wheel', None)
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
                            this = SimpleSketchAPI(self)
                            self._call_sketch_method(handler, this)
                    except Exception:
                        if getattr(self, '_debug_handler_exceptions', False):
                            raise
        except Exception:
            # Best-effort only: do not fail window creation if handlers cannot
            # be registered for platform-specific reasons.
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

    # --- Mouse/input simulation helpers ---------------------------------
    def _ensure_setup(self):
        """Ensure setup() has run on the sketch. If not, run a single frame
        which will execute setup() and capture any setup commands.
        """
        if not getattr(self, '_setup_done', False):
            # run a single frame in headless mode to execute setup
            try:
                self.run_frames(1)
            except Exception:
                # best-effort only
                pass

    def _apply_mouse_update(self, x: Optional[int], y: Optional[int]):
        """Update pmouse/mouse state. If x or y is None, preserve previous.
        pmouse values are set to previous mouse before updating.
        """
        try:
            self.pmouse_x = int(self.mouse_x)
        except Exception:
            self.pmouse_x = 0
        try:
            self.pmouse_y = int(self.mouse_y)
        except Exception:
            self.pmouse_y = 0
        if x is not None:
            try:
                self.mouse_x = int(x)
            except Exception:
                pass
        if y is not None:
            try:
                self.mouse_y = int(y)
            except Exception:
                pass

    def simulate_mouse_press(self, x: Optional[int] = None, y: Optional[int] = None, button: Optional[str] = None, event: Optional[object] = None):
        """Simulate a mouse press. Accepts either primitives (x,y,button)
        or an event-like object. Ensures setup() ran and dispatches
        sketch.mouse_pressed() if present.
        """
        # Lazy normalize event-like objects
        from core.adapters.pyglet_mouse import normalize_event
        ev = normalize_event(event) if event is not None else {}
        ex = ev.get('x', x)
        ey = ev.get('y', y)
        btn = ev.get('button', button)

        self._ensure_setup()
        # Update mouse coordinates and pressed flags
        self._apply_mouse_update(ex, ey)
        self.mouse_pressed = True
        if btn is not None:
            try:
                self.mouse_button = str(btn)
            except Exception:
                pass

        # Dispatch handler on sketch if present
        handler = getattr(self.sketch, 'mouse_pressed', None)
        if callable(handler):
            try:
                # Prefer calling with no arguments so the proxy can invoke
                # the original handler with the correct bound signature.
                return handler()
            except TypeError:
                try:
                    this = SimpleSketchAPI(self)
                    return self._call_sketch_method(handler, this)
                except Exception:
                    if getattr(self, '_debug_handler_exceptions', False):
                        raise
                    return None
            except Exception:
                if getattr(self, '_debug_handler_exceptions', False):
                    raise
                return None

    def simulate_mouse_release(self, x: Optional[int] = None, y: Optional[int] = None, button: Optional[str] = None, event: Optional[object] = None):
        """Simulate mouse release and dispatch sketch.mouse_released/clicked.
        """
        from core.adapters.pyglet_mouse import normalize_event
        ev = normalize_event(event) if event is not None else {}
        ex = ev.get('x', x)
        ey = ev.get('y', y)
        btn = ev.get('button', button)

        self._ensure_setup()
        # Update positions
        self._apply_mouse_update(ex, ey)
        self.mouse_pressed = False
        if btn is not None:
            try:
                self.mouse_button = str(btn)
            except Exception:
                pass

        # Call mouse_released
        released = getattr(self.sketch, 'mouse_released', None)
        if callable(released):
            try:
                try:
                    released()
                except TypeError:
                    this = SimpleSketchAPI(self)
                    self._call_sketch_method(released, this)
            except Exception:
                pass

        # Optionally call mouse_clicked (many frameworks define click as press+release)
        clicked = getattr(self.sketch, 'mouse_clicked', None)
        if callable(clicked):
            try:
                try:
                    clicked()
                except TypeError:
                    this = SimpleSketchAPI(self)
                    self._call_sketch_method(clicked, this)
            except Exception:
                pass

    def simulate_mouse_move(self, x: Optional[int] = None, y: Optional[int] = None, event: Optional[object] = None):
        """Simulate mouse move (no button pressed): updates mouse coords and
        calls mouse_moved if present.
        """
        from core.adapters.pyglet_mouse import normalize_event
        ev = normalize_event(event) if event is not None else {}
        ex = ev.get('x', x)
        ey = ev.get('y', y)

        self._ensure_setup()
        self._apply_mouse_update(ex, ey)

        moved = getattr(self.sketch, 'mouse_moved', None)
        if callable(moved):
            try:
                try:
                    moved()
                except TypeError:
                    this = SimpleSketchAPI(self)
                    self._call_sketch_method(moved, this)
            except Exception:
                pass

    def simulate_mouse_drag(self, x: Optional[int] = None, y: Optional[int] = None, button: Optional[str] = None, event: Optional[object] = None):
        """Simulate mouse drag (move while pressed). Calls mouse_dragged.
        """
        from core.adapters.pyglet_mouse import normalize_event
        ev = normalize_event(event) if event is not None else {}
        ex = ev.get('x', x)
        ey = ev.get('y', y)
        btn = ev.get('button', button)

        self._ensure_setup()
        # Ensure pressed state
        self._apply_mouse_update(ex, ey)
        self.mouse_pressed = True
        if btn is not None:
            try:
                self.mouse_button = str(btn)
            except Exception:
                pass

        dragged = getattr(self.sketch, 'mouse_dragged', None)
        if callable(dragged):
            try:
                try:
                    dragged()
                except TypeError:
                    this = SimpleSketchAPI(self)
                    self._call_sketch_method(dragged, this)
            except Exception:
                pass

    def simulate_mouse_wheel(self, event_or_count: object):
        """Simulate mouse wheel event. Accepts either an event object with
        get_count() or a numeric count directly.
        """
        # Determine count
        count = None
        try:
            if hasattr(event_or_count, 'get_count') and callable(getattr(event_or_count, 'get_count')):
                # call get_count() and coerce safely to int via a dynamically
                # typed intermediate to satisfy static overload resolution.
                _maybe: object = event_or_count.get_count()
                try:
                    # Use a dynamic Any-typed variable so int() overload
                    # resolution succeeds in static analysis.
                    from typing import Any as _Any, cast
                    _val: _Any = _maybe
                    # Cast to an int-compatible type for static checkers, then
                    # coerce at runtime. This is a conservative local workaround
                    # to appease mypy's overload resolution.
                    count = int(cast(int, _val))
                except Exception:
                    count = None
        except Exception:
            count = None
        if count is None:
            try:
                from typing import Any as _Any
                _ec: _Any = event_or_count
                count = int(_ec)
            except Exception:
                # Can't determine count; abort
                return None

        self._ensure_setup()
        handler = getattr(self.sketch, 'mouse_wheel', None)
        if callable(handler):
            try:
                # Many handlers expect an event; provide a tiny shim
                class _Wheel:
                    def __init__(self, c: int):
                        self._c = int(c)
                    def get_count(self) -> int:
                        return int(self._c)

                try:
                    # Prefer calling with the event-like shim
                    return handler(_Wheel(count))
                except TypeError:
                    # Fallback: the handler might expect `this` instead
                    this = SimpleSketchAPI(self)
                    return self._call_sketch_method(handler, this)
            except Exception:
                pass


    # --- 2D Transform / matrix stack helpers ----------------------------
    def _identity_matrix(self):
        """Return a 3x3 identity matrix as a flat list (row-major)."""
        return [1.0, 0.0, 0.0,
                0.0, 1.0, 0.0,
                0.0, 0.0, 1.0]

    def _mul_mat(self, a, b):
        """Multiply two 3x3 matrices (flat row-major lists).

        Returns a new flat list representing a*b.
        """
        return [
            a[0]*b[0] + a[1]*b[3] + a[2]*b[6],
            a[0]*b[1] + a[1]*b[4] + a[2]*b[7],
            a[0]*b[2] + a[1]*b[5] + a[2]*b[8],

            a[3]*b[0] + a[4]*b[3] + a[5]*b[6],
            a[3]*b[1] + a[4]*b[4] + a[5]*b[7],
            a[3]*b[2] + a[4]*b[5] + a[5]*b[8],

            a[6]*b[0] + a[7]*b[3] + a[8]*b[6],
            a[6]*b[1] + a[7]*b[4] + a[8]*b[7],
            a[6]*b[2] + a[7]*b[5] + a[8]*b[8],
        ]

    def _ensure_matrix_stack(self):
        if not hasattr(self, '_matrix_stack'):
            self._matrix_stack = [self._identity_matrix()]

    def push_matrix(self):
        self._ensure_matrix_stack()
        try:
            top = list(self._matrix_stack[-1])
            self._matrix_stack.append(top)
        except Exception:
            # ensure stack has at least one identity
            self._matrix_stack = [self._identity_matrix()]
        try:
            return self.graphics.record('push_matrix')
        except Exception:
            return None

    def pop_matrix(self):
        self._ensure_matrix_stack()
        try:
            if len(self._matrix_stack) > 1:
                self._matrix_stack.pop()
            else:
                # reset to identity if attempting to pop the last
                self._matrix_stack[-1] = self._identity_matrix()
        except Exception:
            self._matrix_stack = [self._identity_matrix()]
        try:
            return self.graphics.record('pop_matrix')
        except Exception:
            return None

    def reset_matrix(self):
        self._ensure_matrix_stack()
        try:
            self._matrix_stack[-1] = self._identity_matrix()
        except Exception:
            self._matrix_stack = [self._identity_matrix()]
        try:
            return self.graphics.record('reset_matrix')
        except Exception:
            return None

    def _apply_transform_matrix(self, mat):
        """Right-multiply the current matrix by mat (both flat 3x3 lists)."""
        self._ensure_matrix_stack()
        try:
            cur = self._matrix_stack[-1]
            self._matrix_stack[-1] = self._mul_mat(cur, mat)
        except Exception:
            self._matrix_stack[-1] = list(mat)

    def translate(self, x: float, y: float, z: Optional[float] = None):
        try:
            tx = float(x)
            ty = float(y)
        except Exception:
            return None
        mat = [1.0, 0.0, tx,
               0.0, 1.0, ty,
               0.0, 0.0, 1.0]
        self._apply_transform_matrix(mat)
        try:
            return self.graphics.record('translate', x=tx, y=ty)
        except Exception:
            return None

    def rotate(self, angle: float):
        import math
        try:
            a = float(angle)
        except Exception:
            return None
        c = math.cos(a)
        s = math.sin(a)
        mat = [c, -s, 0.0,
               s,  c, 0.0,
               0.0,0.0,1.0]
        self._apply_transform_matrix(mat)
        try:
            return self.graphics.record('rotate', angle=float(a))
        except Exception:
            return None

    def scale(self, sx: float, sy: Optional[float] = None, sz: Optional[float] = None):
        try:
            sx_f = float(sx)
            sy_f = float(sy) if sy is not None else sx_f
        except Exception:
            return None
        mat = [sx_f, 0.0, 0.0,
               0.0, sy_f, 0.0,
               0.0, 0.0, 1.0]
        self._apply_transform_matrix(mat)
        try:
            return self.graphics.record('scale', sx=sx_f, sy=sy_f)
        except Exception:
            return None

    def shear_x(self, angle: float):
        import math
        try:
            a = float(angle)
        except Exception:
            return None
        mat = [1.0, math.tan(a), 0.0,
               0.0, 1.0,        0.0,
               0.0, 0.0,        1.0]
        self._apply_transform_matrix(mat)
        try:
            return self.graphics.record('shear_x', angle=float(a))
        except Exception:
            return None

    def shear_y(self, angle: float):
        import math
        try:
            a = float(angle)
        except Exception:
            return None
        mat = [1.0, 0.0,        0.0,
               math.tan(a), 1.0, 0.0,
               0.0, 0.0,        1.0]
        self._apply_transform_matrix(mat)
        try:
            return self.graphics.record('shear_y', angle=float(a))
        except Exception:
            return None

    def apply_matrix(self, *args):
        """Apply a provided matrix to the current transform.

        Accepts either a single sequence-like of 9 or 6 numbers, or 6/9 numbers
        as individual arguments. For 6 numbers we expand them into a 3x3
        affine matrix with a bottom row [0,0,1].
        """
        vals = None
        if len(args) == 1:
            maybe = args[0]
            try:
                # sequence-like
                vals = list(maybe)
            except Exception:
                vals = None
        else:
            vals = list(args)

        if vals is None:
            return None

        try:
            if len(vals) == 6:
                # assume [a,b,c,d,e,f] -> 3x3: [a,b,c, d,e,f, 0,0,1]
                mat = [float(vals[0]), float(vals[1]), float(vals[2]),
                       float(vals[3]), float(vals[4]), float(vals[5]),
                       0.0, 0.0, 1.0]
                self._apply_transform_matrix(mat)
            elif len(vals) == 9:
                mat = [float(v) for v in vals]
                self._apply_transform_matrix(mat)
            elif len(vals) == 16:
                # Accept 4x4 matrix (row-major). For 2D engine we won't
                # attempt a full 4x4 -> 3x3 conversion; just record values
                # so headless tests can observe the call. Do not modify
                # the engine matrix stack for 4x4 inputs.
                mat = [float(v) for v in vals]
            else:
                return None
        except Exception:
            return None

        try:
            return self.graphics.record('apply_matrix', matrix=mat)
        except Exception:
            return None


