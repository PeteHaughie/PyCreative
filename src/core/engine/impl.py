"""Minimal headless Engine implementation for tests and development.

This implementation focuses on headless execution: it records drawing
commands to an in-memory buffer (`graphics.commands`) so tests can assert
behaviour without opening windows or touching GPU libraries.

Not a production implementation — replace with real Engine when ready.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class APIRegistry:
    def __init__(self):
        self._map: Dict[str, Callable] = {}

    def register(self, name: str, fn: Callable):
        self._map[name] = fn

    def get(self, name: str):
        return self._map.get(name)


@dataclass
class GraphicsBuffer:
    commands: List[Dict[str, Any]] = field(default_factory=list)

    def clear(self):
        self.commands.clear()

    def record(self, op: str, **kwargs):
        self.commands.append({'op': op, 'args': kwargs})


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
        self.frame_rate = 60
        self.frame_count = 0
        # default size (can be overridden by sketch.size())
        self.width = 640
        self.height = 480
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
                self.sketch = s.Sketch()
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
        try:
            return fn(this)
        except TypeError:
            # try calling without args
            return fn()

    def run_frames(self, n: int = 1):
        for _ in range(n):
            self.step_frame()

    # Engine-side helpers used by SimpleSketchAPI
    def _set_size(self, w: int, h: int):
        self.width = int(w)
        self.height = int(h)

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

