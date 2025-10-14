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


class Engine:
    """A tiny headless engine for testing sketches.

    Lifecycle behaviour implemented:
    - call `setup(this)` once before the first draw
    - call `draw(this)` each frame depending on loop/no_loop/redraw
    - expose minimal helpers: size, no_loop, loop, redraw, save_frame
    """

    def __init__(self, sketch_module: Optional[Any] = None, headless: bool = True):
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
        self.snapshot_backend: Optional[Callable[[
            str, int, int, "Engine"], None]] = None

        # Normalize sketch: if a module contains a `Sketch` class, instantiate it
        self._normalize_sketch()

        self._running = False

        # register a minimal drawing API for sketches to call (delegates to core.shape)
        try:
            import core.shape as _shape
            self.api.register('rect', lambda x, y, w, h, **kwargs: _shape.rect(self, x, y, w, h, **kwargs))
            self.api.register('line', lambda x1, y1, x2, y2, **kwargs: _shape.line(self, x1, y1, x2, y2, **kwargs))
            self.api.register('square', lambda x, y, size, **kwargs: _shape.square(self, x, y, size, **kwargs))
            self.api.register('stroke_weight', lambda w: _shape.stroke_weight(self, w))
        except Exception:
            # In constrained/test environments the shape module may be unavailable;
            # fallback to simple inline recorders.
            self.api.register('rect', lambda x, y, w, h, **kwargs: self.graphics.record('rect', x=x, y=y, w=w, h=h, **kwargs))
            self.api.register('line', lambda x1, y1, x2, y2, **kwargs: self.graphics.record('line', x1=x1, y1=y1, x2=x2, y2=y2, **kwargs))

        # register environment helpers (size, frame_rate, etc.) from core.environment
        try:
            import core.environment as _env
            # register getters/setters and functions under their spec names
            self.api.register('size', lambda w, h: _env.size(self, w, h))
            self.api.register('frame_rate', lambda fps=None: _env.frame_rate(self, fps))
            self.api.register('frame_count', lambda: _env.frame_count(self))
            self.api.register('delay', lambda ms: _env.delay(self, ms))
            self.api.register('pixel_density', lambda d=None: _env.pixel_density(self, d))
            self.api.register('pixel_width', lambda: _env.pixel_width(self))
            self.api.register('pixel_height', lambda: _env.pixel_height(self))
            self.api.register('display_width', lambda: _env.display_width(self))
            self.api.register('display_height', lambda: _env.display_height(self))
            self.api.register('fullscreen', lambda display=None: _env.fullscreen(self, display))
            self.api.register('cursor', lambda *a, **k: _env.cursor(self, *a, **k))
            self.api.register('no_cursor', lambda: _env.no_cursor(self))
            self.api.register('window_move', lambda x, y: _env.window_move(self, x, y))
            self.api.register('window_ratio', lambda w, h: _env.window_ratio(self, w, h))
            self.api.register('window_resizeable', lambda r: _env.window_resizeable(self, r))
            self.api.register('window_title', lambda t: _env.window_title(self, t))
        except Exception:
            # If the environment module is unavailable in a constrained test
            # environment, skip registration silently.
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
                # Attach a SimpleSketchAPI facade onto the instance so class-based
                # sketches can call self.size(), self.background(), etc.
                api = SimpleSketchAPI(self)
                for name in ('size', 'background', 'no_loop', 'loop', 'redraw', 'save_frame', 'rect', 'line', 'frame_rate'):
                    if not hasattr(inst, name):
                        try:
                            setattr(inst, name, getattr(api, name))
                        except Exception:
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
        self.graphics.clear()
        if self.sketch is None:
            return

        # run setup once
        if not self._setup_done:
            this = SimpleSketchAPI(self)
            setup = getattr(self.sketch, 'setup', None)
            if callable(setup):
                self._call_sketch_method(setup, this)
            self._setup_done = True

        # decide whether to run draw this frame
        should_draw = False
        if self.looping:
            should_draw = True
        elif self._redraw_requested:
            should_draw = True

        if not should_draw:
            return

        # Note: do not auto-insert a default background here. If a sketch
        # wants a background it should call `this.background()` in setup()
        # or draw(). This keeps recorded command order intuitive for tests
        # and user code (drawn shapes appear in the same order they were
        # emitted).
        this = SimpleSketchAPI(self)

        draw = getattr(self.sketch, 'draw', None)
        if callable(draw):
            self._call_sketch_method(draw, this)

        # reset one-shot redraw request
        if self._redraw_requested:
            self._redraw_requested = False

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

    def run_frames(self, n: int = 1):
        import time

        for _ in range(n):
            start = time.perf_counter()
            self.step_frame()
            # enforce frame rate if requested and running in non-headless mode
            if self.frame_rate > 0 and not self.headless:
                elapsed = time.perf_counter() - start
                target = 1.0 / float(self.frame_rate)
                to_sleep = target - elapsed
                if to_sleep > 0:
                    time.sleep(to_sleep)

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
                self.run_frames(max_frames)
            return

        # Lazy-import pyglet to avoid import-time dependency in tests
        try:
            import pyglet
            from pyglet import gl
            from pyglet import shapes
        except Exception as exc:  # pragma: no cover - platform specific
            raise RuntimeError('pyglet is required for windowed mode') from exc

        # create window
        self._window = pyglet.window.Window(
            width=self.width, height=self.height, vsync=True)
        try:
            print(
                f'Engine: created window {self._window} size=({self.width},{self.height})')
        except Exception:
            pass

        # internal frame counter to stop after max_frames. When max_frames is
        # None we set it to a very large number so the scheduled update keeps
        # running until the user explicitly closes the window.
        self._frames_left = float(
            'inf') if max_frames is None else int(max_frames)

        # set clear color from current background
        r, g, b = self.background_color
        gl.glClearColor(r / 255.0, g / 255.0, b / 255.0, 1.0)

        @self._window.event
        def on_draw():
            self._window.clear()
            # create a local batch per-frame to avoid accumulating shape objects
            local_batch = pyglet.graphics.Batch()
            for cmd in self.graphics.commands:
                op = cmd.get('op')
                args = cmd.get('args', {})
                if op == 'rect':
                    x = args.get('x', 0)
                    y = args.get('y', 0)
                    w = args.get('w', 0)
                    h = args.get('h', 0)
                    # choose fill color if present, otherwise transparent
                    fill = args.get('fill')
                    stroke = args.get('stroke')
                    color = fill if fill is not None else (255, 255, 255)
                    shapes.Rectangle(x, y, w, h, color=color,
                                     batch=local_batch)
                elif op == 'line':
                    x1 = args.get('x1', 0)
                    y1 = args.get('y1', 0)
                    x2 = args.get('x2', 0)
                    y2 = args.get('y2', 0)
                    lw = args.get('stroke_weight', 1)
                    color = args.get('stroke', (0, 0, 0))
                    shapes.Line(x1, y1, x2, y2, width=lw,
                                color=color, batch=local_batch)
            local_batch.draw()

        def update(dt):
            try:
                print(
                    f'Engine:update called dt={dt} frames_left={self._frames_left}')
            except Exception:
                pass
            # step the sketch to populate graphics.commands
            self.step_frame()
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

        # run the app (blocks until exit)
        try:
            print('Engine: entering pyglet.app.run()')
        except Exception:
            pass
        pyglet.app.run()
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
