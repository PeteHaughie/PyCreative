"""Minimal headless Engine implementation for tests and development.

This implementation focuses on headless execution: it records drawing
commands to an in-memory buffer (`graphics.commands`) so tests can assert
behaviour without opening windows or touching GPU libraries.

Not a production implementation — replace with real Engine when ready.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from .graphics import GraphicsBuffer
from .color import hsb_to_rgb


from .api_registry import APIRegistry


# GraphicsBuffer moved to src/core/engine/graphics.py


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
        self.snapshot_backend: Optional[Callable[[str, int, int, "Engine"], None]] = None

        # Normalize sketch: if a module contains a `Sketch` class, instantiate it
        self._normalize_sketch()

        self._running = False

        # register a minimal drawing API for sketches to call
        self.api.register('rect', lambda x, y, w, h, **kwargs: self.graphics.record('rect', x=x, y=y, w=w, h=h, **kwargs))
        self.api.register('line', lambda x1, y1, x2, y2, **kwargs: self.graphics.record('line', x1=x1, y1=y1, x2=x2, y2=y2, **kwargs))

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

        # ensure a background is recorded for this frame. Allow setup() to
        # set size/background first; if no background op exists after setup,
        # record the default/background set on the engine.
        this = SimpleSketchAPI(self)
        # if user code called background() during setup it will have added an op
        has_background = any(c.get('op') == 'background' for c in self.graphics.commands)
        if not has_background:
            # record the current background color
            r, g, b = self.background_color
            self.graphics.record('background', r=r, g=g, b=b)

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
        self._window = pyglet.window.Window(width=self.width, height=self.height, vsync=True)
        try:
            print(f'Engine: created window {self._window} size=({self.width},{self.height})')
        except Exception:
            pass

        # internal frame counter to stop after max_frames. When max_frames is
        # None we set it to a very large number so the scheduled update keeps
        # running until the user explicitly closes the window.
        self._frames_left = float('inf') if max_frames is None else int(max_frames)

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
                    shapes.Rectangle(x, y, w, h, color=color, batch=local_batch)
                elif op == 'line':
                    x1 = args.get('x1', 0)
                    y1 = args.get('y1', 0)
                    x2 = args.get('x2', 0)
                    y2 = args.get('y2', 0)
                    lw = args.get('stroke_weight', 1)
                    color = args.get('stroke', (0, 0, 0))
                    shapes.Line(x1, y1, x2, y2, width=lw, color=color, batch=local_batch)
            local_batch.draw()

        def update(dt):
            try:
                print(f'Engine:update called dt={dt} frames_left={self._frames_left}')
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
        interval = None if self.frame_rate < 1 else 1.0 / float(self.frame_rate)
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
        # If a custom snapshot backend is provided, prefer it
        if self.snapshot_backend is not None:
            try:
                self.snapshot_backend(path, self.width, self.height, self)
                self.graphics.record('save_frame', path=path, backend='custom')
                return
            except Exception:
                # fall through to default behaviour
                pass

        try:
            from PIL import Image
            img = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 255))
            img.save(path)
            self.graphics.record('save_frame', path=path, backend='pillow')
        except Exception:
            # fallback: just record the request (no file written)
            self.graphics.record('save_frame', path=path, backend='none')


def _hsb_to_rgb(h: float, s: float, b: float):
    """Convert HSB/HSV values in range 0-255 (or 0-1) to an (r,g,b) tuple 0-255.

    Accepts either 0-1 floats or 0-255 ints; returns three ints 0-255.
    """
    # normalize inputs to 0-1
    def norm(v):
        return v / 255.0 if v > 1 else float(v)

    H = norm(h)
    S = norm(s)
    V = norm(b)

    if S == 0:
        r = g = b = int(round(V * 255))
        return (r, g, b)

    i = int(H * 6)  # sector 0..5
    f = (H * 6) - i
    p = V * (1 - S)
    q = V * (1 - S * f)
    t = V * (1 - S * (1 - f))

    i = i % 6
    if i == 0:
        r_, g_, b_ = V, t, p
    elif i == 1:
        r_, g_, b_ = q, V, p
    elif i == 2:
        r_, g_, b_ = p, V, t
    elif i == 3:
        r_, g_, b_ = p, q, V
    elif i == 4:
        r_, g_, b_ = t, p, V
    else:
        r_, g_, b_ = V, p, q

    return (int(round(r_ * 255)), int(round(g_ * 255)), int(round(b_ * 255)))


class SimpleSketchAPI:
    """Lightweight object passed to sketches as `this`.

    It offers convenience methods that delegate to the Engine's API registry
    and control lifecycle behaviour (size/no_loop/loop/redraw/save_frame).
    """

    def __init__(self, engine: Engine):
        self._engine = engine

    def rect(self, x, y, w, h, **kwargs):
        fn = self._engine.api.get('rect')
        if fn:
            return fn(x, y, w, h, **kwargs)

    # lifecycle and environment helpers exposed to sketches
    def size(self, w: int, h: int):
        """Set sketch size (should be called in setup())."""
        self._engine._set_size(w, h)

    def frame_rate(self, n: int):
        """Set frame rate. Use -1 for unrestricted."""
        try:
            self._engine.frame_rate = int(n)
        except Exception:
            raise TypeError('frame_rate expects an integer')

    def background(self, *args):
        """Set background color. Accepts single grayscale, RGB (3) or HSB depending on color_mode.

        In 'RGB' mode inputs are treated as 0-255 RGB. In 'HSB' mode inputs are
        treated as H,S,B either 0-1 or 0-255 and converted to RGB.
        """
        mode = getattr(self._engine, 'color_mode', 'RGB')

        if len(args) == 1:
            v = args[0]
            if isinstance(v, (tuple, list)) and len(v) == 3:
                vals = v
            else:
                vals = (int(v), int(v), int(v))
        elif len(args) == 3:
            vals = args
        else:
            raise TypeError('background() expects 1 or 3 arguments')

        if str(mode).upper() == 'HSB':
            r, g, b = hsb_to_rgb(*vals)
        else:
            r, g, b = (int(vals[0]), int(vals[1]), int(vals[2]))

        # update engine background color and record op
        self._engine.background_color = (int(r), int(g), int(b))
        self._engine.graphics.record('background', r=int(r), g=int(g), b=int(b))

    def no_loop(self):
        self._engine._no_loop()

    def loop(self):
        self._engine._loop()

    def redraw(self):
        self._engine._redraw()

    def save_frame(self, path: str):
        self._engine._save_frame(path)

    def line(self, x1, y1, x2, y2, **kwargs):
        fn = self._engine.api.get('line')
        if fn:
            return fn(x1, y1, x2, y2, **kwargs)

    # new drawing state helpers
    def fill(self, *args):
        """Set fill color respecting color_mode (RGB or HSB)."""
        mode = getattr(self._engine, 'color_mode', 'RGB')
        if len(args) == 1:
            v = args[0]
            if isinstance(v, (tuple, list)) and len(v) == 3:
                vals = v
            else:
                vals = (int(v), int(v), int(v))
        elif len(args) == 3:
            vals = args
        else:
            raise TypeError('fill() expects 1 or 3 args')

        if str(mode).upper() == 'HSB':
            self._engine.fill_color = hsb_to_rgb(*vals)
        else:
            self._engine.fill_color = (int(vals[0]), int(vals[1]), int(vals[2]))

    def stroke(self, *args):
        """Set stroke color respecting color_mode (RGB or HSB)."""
        mode = getattr(self._engine, 'color_mode', 'RGB')
        if len(args) == 1:
            v = args[0]
            if isinstance(v, (tuple, list)) and len(v) == 3:
                vals = v
            else:
                vals = (int(v), int(v), int(v))
        elif len(args) == 3:
            vals = args
        else:
            raise TypeError('stroke() expects 1 or 3 args')

        if str(mode).upper() == 'HSB':
            self._engine.stroke_color = hsb_to_rgb(*vals)
        else:
            self._engine.stroke_color = (int(vals[0]), int(vals[1]), int(vals[2]))

    def stroke_weight(self, w: int):
        self._engine.stroke_weight = int(w)

    def square(self, x, y, size, **kwargs):
        # delegate to rect with equal width/height; also forward drawing state
        fill = kwargs.pop('fill', None)
        stroke = kwargs.pop('stroke', None)
        sw = kwargs.pop('stroke_weight', None)
        # prefer explicit args, otherwise use engine state
        if fill is None:
            fill = self._engine.fill_color
        if stroke is None:
            stroke = self._engine.stroke_color
        if sw is None:
            sw = self._engine.stroke_weight
        fn = self._engine.api.get('rect')
        if fn:
            return fn(x, y, size, size, fill=fill, stroke=stroke, stroke_weight=sw)

