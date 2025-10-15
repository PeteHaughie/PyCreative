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


class Engine:
    """A tiny headless engine for testing sketches.

    Lifecycle behaviour implemented:
    - call `setup(this)` once before the first draw
    - call `draw(this)` each frame depending on loop/no_loop/redraw
    - expose minimal helpers: size, no_loop, loop, redraw, save_frame
    """

    def __init__(self, sketch_module: Optional[Any] = None, headless: bool = True):
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
                # expose a broader set of convenience methods to Sketch instances
                for name in (
                    'size', 'background', 'no_loop', 'loop', 'redraw', 'save_frame',
                    'rect', 'line', 'square', 'frame_rate',
                    'fill', 'stroke', 'stroke_weight'
                ):
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
            self._setup_commands = list(self.graphics.commands)
            self._setup_done = True
            print("[DEBUG] Playing setup commands:", self._setup_commands)
        # If no_loop and already drawn, return immediately before any draw logic
        if not self.looping and getattr(self, '_no_loop_drawn', False):
            return
        else:
            self.graphics.clear()
            # Prepend setup commands to graphics.commands for each frame
            self.graphics.commands = list(self._setup_commands)

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
            print("[DEBUG] No sketch attached to engine.")
            return

        # run setup once
        if not self._setup_done:
            this = SimpleSketchAPI(self)
            setup = getattr(self.sketch, 'setup', None)
            if callable(setup):
                self._call_sketch_method(setup, this)
            self._setup_done = True

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
            print("[DEBUG] draw is not callable.")

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

        # If looping is disabled, mark that we've run the one-shot draw so
        # subsequent frames are skipped early.
        if not self.looping:
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

    def run_frames(self, n: int = 1):
        import time

        frame_counter = 0
        while frame_counter < n:
            # Stop if no_loop has already drawn
            if not self.looping and getattr(self, '_no_loop_drawn', False):
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
        # Setup is now handled in step_frame; do not run it here

        # create window using potentially updated size from setup()
        self._window = pyglet.window.Window(
            width=self.width, height=self.height, vsync=True)
        try:
            print(
                f'Engine: created window {self._window} size=({self.width},{self.height})')
        except Exception:
            pass
        # running until the user explicitly closes the window.
        self._frames_left = float(
            'inf') if max_frames is None else int(max_frames)

        @self._window.event
        def on_draw():
            # DEBUG: Print graphics.commands before rendering
            # print("[DEBUG] graphics.commands before render:", self.graphics.commands)
            presenter = SkiaGLPresenter(self.width, self.height)
            replay_fn = presenter.replay_fn
            presenter.render_commands(self.graphics.commands, replay_fn)
            presenter.present()

            texture = wrap_gl_texture(presenter.tex_id, presenter.width, presenter.height)
            if texture:
                texture.blit(0, 0)
        
        def wrap_gl_texture(tex_id, width, height):
            from pyglet import image
            texture = image.Texture(width, height, image.GL_TEXTURE_2D, tex_id)
            return texture

        def update(dt):
            # Stop if no_loop has already drawn
            if not self.looping and getattr(self, '_no_loop_drawn', False):
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
