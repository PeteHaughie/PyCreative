from __future__ import annotations

from typing import Optional, Tuple, Callable, Any, cast
from collections.abc import Iterable
from .types import ColorOrNone, ColorTupleOrNone, ColorInput

import time
import os
import pygame
import math

from . import input as input_mod
from .graphics import Surface as GraphicsSurface
from .graphics import OffscreenSurface
from .assets import Assets

# Sentinel for pending state fields so we can distinguish "no pending value"
# from an explicit `None` which means "disable this style" (e.g., no_fill()).
_PENDING_UNSET = object()


class Sketch:
    """Minimal Sketch runtime: lifecycle hooks and a pygame-based run loop.

    This is intentionally small and focused on the lifecycle and basic drawing helpers
    so examples and tests can run during bootstrapping.
    """
    # Backwards-compatible shorthand constants used by many examples: allow
    # sketches to refer to `self.CENTER` / `self.CORNER` when setting modes.
    CENTER = GraphicsSurface.MODE_CENTER
    CORNER = GraphicsSurface.MODE_CORNER
    # Expose blend mode constants so sketches can call self.BLEND / self.ADD etc.
    BLEND = GraphicsSurface.BLEND
    ADD = GraphicsSurface.ADD
    SUBTRACT = GraphicsSurface.SUBTRACT
    DARKEST = GraphicsSurface.DARKEST
    LIGHTEST = GraphicsSurface.LIGHTEST
    DIFFERENCE = GraphicsSurface.DIFFERENCE
    EXCLUSION = GraphicsSurface.EXCLUSION
    MULTIPLY = GraphicsSurface.MULTIPLY
    SCREEN = GraphicsSurface.SCREEN
    REPLACE = GraphicsSurface.REPLACE

    def __init__(self, sketch_path: Optional[str] = None, seed: int | None = None) -> None:
        # Optional path to the user sketch file that instantiated this Sketch
        self.sketch_path: Optional[str] = sketch_path
        self.width: int = 640
        self.height: int = 480
        self.fullscreen: bool = False
        self._frame_rate: int = 60
        self._surface: Optional[pygame.Surface] = None
        # High-level wrapper for drawing primitives
        self.surface: Optional[GraphicsSurface] = None
        # Assets manager (initialized when running the sketch)
        self.assets: Optional[Assets] = None
        self._clock: Optional[pygame.time.Clock] = None
        self._running: bool = False
        self.frame_count: int = 0
        self._title: str = "PyCreative"
        # Generic cache store for sketches (used by cached graphics helpers)
        self._cache_store: dict = {}
        # Pending drawing state if user sets it before the Surface is created.
        # Use a sentinel to distinguish "no pending change" from an explicit
        # `None` (which means disable fill/stroke). Narrow types where possible
        # using the shared ColorLike alias.
        self._pending_fill: ColorOrNone | Any = _PENDING_UNSET
        self._pending_stroke: ColorOrNone | Any = _PENDING_UNSET
        self._pending_stroke_weight: int | Any = _PENDING_UNSET
        # Pending cursor visibility state: use sentinel to distinguish
        # "no pending change" from an explicit show/hide request.
        self._pending_cursor: bool | Any = _PENDING_UNSET
        # By default, pressing Escape closes the sketch; this can be disabled
        # by calling `self.set_escape_closes(False)` in the sketch.
        self._escape_closes = True
        # Pending shape mode state for rect/ellipse - allow setting in setup()
        self._pending_rect_mode: Optional[str] | Any = _PENDING_UNSET
        self._pending_ellipse_mode: Optional[str] | Any = _PENDING_UNSET
        # Pending color mode (e.g., set in setup before surface exists)
        self._pending_color_mode: tuple | Any = _PENDING_UNSET
        # Pending image mode/tint recorded before surface exists
        self._pending_image_mode: Optional[str] | Any = _PENDING_UNSET
        self._pending_tint: tuple | Any = _PENDING_UNSET
        # Pending blend mode
        self._pending_blend: Optional[str] | Any = _PENDING_UNSET
        # Pending line cap / join style (butt, round, square) / (miter, round, bevel)
        self._pending_line_cap: Optional[str] | Any = _PENDING_UNSET
        self._pending_line_join: Optional[str] | Any = _PENDING_UNSET
        # Pending background/clear color set in setup() before surface exists
        self._pending_background: ColorOrNone | Any = _PENDING_UNSET

        # Runtime no-loop control (if True, draw() runs once then is suppressed)
        self._no_loop_mode = False
        self._has_drawn_once = False

        # Optional per-sketch snapshots folder (preferred over env var)
        # Can be set by assignment: `self.save_folder = 'snapshots'` or via
        # the helper `self.set_save_folder('snapshots')`.
        # Use a plain assignment (no forward annotation) to avoid static
        # analysis issues in older type-checkers.
        self._save_folder: Optional[str] = None
        # Display options: double buffering and vsync
        # - double buffering reduces tearing and is recommended for smooth updates
        # - vsync requests buffer swap synchronization with the display; support
        #   depends on the underlying SDL2/Pygame build and platform.
        self._double_buffer: bool = True
        # vsync: 0 = disabled, 1 = enabled. Use None/0 for no vsync.
        self._vsync: int = 0
        # Key/input convenience state (matches Processing-style helpers)
        # - `key` is the readable key name (e.g., 'a', 'space') when available
        # - `key_code` is the numeric pygame key constant (e.g., pygame.K_SPACE)
        # - `key_is_pressed` is True while a key is down
        self.key = None
        self.key_code = None
        self.key_is_pressed = False
        # Mouse convenience state (set by input.dispatch_event)
        # Public read-only helpers `mouse_x` / `mouse_y` expose these values.
        self._mouse_x: Optional[int] = None
        self._mouse_y: Optional[int] = None
        # previous mouse coords (public fields kept for compatibility)
        self.pmouse_x: Optional[int] = None
        self.pmouse_y: Optional[int] = None
        # Provide a small Processing-like math facade on the Sketch instance
        # so sketches can use `self.math.cos(...)` or `self.PI` without
        # depending on the stdlib math module directly. The module is
        # implemented in `pycreative.pmath`.
        try:
            from . import pmath

            # pmath exposes small math helpers used by sketches. Annotate as
            # Any to satisfy type-checkers here; the runtime assignment can be
            # either the pmath module or stdlib math as a fallback.
            self.math: Any = pmath
            self.PI = pmath.PI
            self.TWO_PI = pmath.TWO_PI
            self.HALF_PI = pmath.HALF_PI
        except Exception:
            # Fall back to stdlib math if pmath can't be imported for any reason
            self.math = math
            self.PI = math.pi
            self.TWO_PI = 2.0 * math.pi
            self.HALF_PI = 0.5 * math.pi
        # Which mouse button (if any) and whether a button is pressed
        self.mouse_button: Optional[int] = None
        self.mouse_is_pressed: bool = False

        # Internal lifecycle flag: True once the runtime has finished running
        # setup(), created the display/surface, and applied pending state.
        # Default to True to preserve existing behavior where dispatch_event
        # delivers events immediately for sketches instantiated in tests or
        # interactive flows. When initialize() runs, it will temporarily
        # mark the sketch as not-ready while setup/display creation are in
        # progress and then set this flag True and flush any queued events.
        self._setup_complete: bool = True
        # Queue of raw pygame.Event objects received before the sketch is
        # ready. This is used by the input dispatcher to buffer and the run()
        # loop to flush after initialization.
        self._pending_event_queue: list = []

        # Apply optional seed for deterministic behavior if provided.
        # Use the random_seed helper which seeds Python's random module.
        if seed is not None:
            try:
                self.random_seed(seed)
            except Exception:
                # best-effort: ignore seed errors
                pass

        # Provide a pvector factory on the instance that is callable and
        # exposes class-style helpers like sub/add/mult/div/dot/angleBetween.
        try:
            # Import only for runtime; TYPE_CHECKING import below helps static analyzers
            from .vector import PVector

            class _PVectorFactoryInst:
                def __call__(self, x: float = 0.0, y: float = 0.0) -> "PVector":
                    # Accept None values (common when mouse pos isn't available)
                    x_val = 0.0 if x is None else float(x)
                    y_val = 0.0 if y is None else float(y)
                    return PVector(x_val, y_val)

                @staticmethod
                def sub(*args):
                    """Support sub(a, b) or sub([a, b])."""
                    def _to_xy(x):
                        if isinstance(x, PVector):
                            return x.x, x.y
                        if hasattr(x, "__iter__"):
                            vals = list(x)
                            if len(vals) >= 2:
                                return float(vals[0]), float(vals[1])
                        raise TypeError("Expected a PVector or 2-length iterable")

                    if len(args) == 2:
                        a, b = args
                        ax, ay = _to_xy(a)
                        bx, by = _to_xy(b)
                        return PVector(ax - bx, ay - by)
                    if len(args) == 1:
                        pair = args[0]
                        # If caller accidentally passed a single PVector (common misuse),
                        # raise a helpful message guiding them to use the instance method.
                        if isinstance(pair, PVector):
                            raise TypeError("pvector.sub requires two vector arguments; to mutate an existing vector use v.sub(other).")
                        if hasattr(pair, "__iter__"):
                            lst = list(pair)
                            if len(lst) == 2:
                                ax, ay = _to_xy(lst[0])
                                bx, by = _to_xy(lst[1])
                                return PVector(ax - bx, ay - by)
                        raise TypeError("pvector.sub requires two vector arguments or a single iterable of two vectors. For mutating subtraction use v.sub(other).")
                    raise TypeError("pvector.sub requires two arguments")

                @staticmethod
                def add(*args):
                    """Support add(a, b) or add([a, b])."""
                    def _to_xy(x):
                        if isinstance(x, PVector):
                            return x.x, x.y
                        if hasattr(x, "__iter__"):
                            vals = list(x)
                            if len(vals) >= 2:
                                return float(vals[0]), float(vals[1])
                        raise TypeError("Expected a PVector or 2-length iterable")

                    if len(args) == 2:
                        a, b = args
                        ax, ay = _to_xy(a)
                        bx, by = _to_xy(b)
                        return PVector(ax + bx, ay + by)
                    if len(args) == 1:
                        pair = args[0]
                        if isinstance(pair, PVector):
                            raise TypeError("pvector.add requires two vector arguments; to mutate an existing vector use v.add(other).")
                        if hasattr(pair, "__iter__"):
                            lst = list(pair)
                            if len(lst) == 2:
                                ax, ay = _to_xy(lst[0])
                                bx, by = _to_xy(lst[1])
                                return PVector(ax + bx, ay + by)
                        raise TypeError("pvector.add requires two vector arguments or a single iterable of two vectors. For mutating addition use v.add(other).")
                    raise TypeError("pvector.add requires two arguments")

                @staticmethod
                def random2d() -> "PVector":
                    """Return a new unit PVector pointing in a random 2D direction.

                    Delegates to `PVector.random2d()` so callers can use
                    `self.pvector.random2d()`.
                    """
                    return PVector.random2d()

                @staticmethod
                def from_angle(theta: float, target=None) -> "PVector":
                    """Create a PVector from an angle; forwards to PVector.from_angle.

                    Prefer snake_case API (project convention).
                    """
                    return PVector.from_angle(theta, target)

                @staticmethod
                def mult(v, scalar: float):
                    vx, vy = (v.x, v.y) if isinstance(v, PVector) else (float(v[0]), float(v[1]))
                    s = float(scalar)
                    return PVector(vx * s, vy * s)

                @staticmethod
                def div(v, scalar: float):
                    vx, vy = (v.x, v.y) if isinstance(v, PVector) else (float(v[0]), float(v[1]))
                    s = float(scalar)
                    if s == 0.0:
                        return PVector(vx, vy)
                    return PVector(vx / s, vy / s)

                @staticmethod
                def dot(a, b):
                    ax, ay = (a.x, a.y) if isinstance(a, PVector) else (float(a[0]), float(a[1]))
                    bx, by = (b.x, b.y) if isinstance(b, PVector) else (float(b[0]), float(b[1]))
                    return ax * bx + ay * by

                @staticmethod
                def dist(a, b):
                    """Euclidean distance between two PVectors or 2-length iterables."""
                    ax, ay = (a.x, a.y) if isinstance(a, PVector) else (float(a[0]), float(a[1]))
                    bx, by = (b.x, b.y) if isinstance(b, PVector) else (float(b[0]), float(b[1]))
                    return math.hypot(ax - bx, ay - by)

                @staticmethod
                def angle_between(a, b):
                    ax, ay = (a.x, a.y) if isinstance(a, PVector) else (float(a[0]), float(a[1]))
                    bx, by = (b.x, b.y) if isinstance(b, PVector) else (float(b[0]), float(b[1]))
                    mag_a = math.hypot(ax, ay)
                    mag_b = math.hypot(bx, by)
                    if mag_a == 0.0 or mag_b == 0.0:
                        return 0.0
                    cosv = (ax * bx + ay * by) / (mag_a * mag_b)
                    cosv = max(-1.0, min(1.0, cosv))
                    return math.acos(cosv)

            # attach factory instance to sketch instance; this shadows the
            # `pvector` method so code can call `self.pvector.sub(...)` and
            # `self.pvector(x,y)` interchangeably.
            try:
                # annotate as Any to avoid signature mismatch warnings from static checkers
                self.pvector: Any = _PVectorFactoryInst()
            except Exception:
                # if assignment fails for any reason, leave method-based behavior
                pass
        except Exception:
            # ignore failures; the pvector() method will still work as a fallback
            pass

    # --- Key hooks (override in sketches) ---
    def key_pressed(self) -> None:
        """Called when a key is pressed (KEYDOWN). Override in sketches."""
        return None

    def key_released(self) -> None:
        """Called when a key is released (KEYUP). Override in sketches."""
        return None

    # Ensure lightweight subclass authoring: when a user defines a Sketch subclass
    # they shouldn't need to re-declare no-op lifecycle helpers like on_event
    # or teardown just to satisfy tooling/tests. Implement __init_subclass__ to
    # copy default implementations into the subclass namespace when missing.
    REQUIRED_METHODS = {
        "setup",
        "update",
        "draw",
        "on_event",
        "teardown",
        "size",
        "frame_rate",
    }

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Copy default methods from Sketch into subclass __dict__ if absent.
        for name in Sketch.REQUIRED_METHODS:
            if name not in cls.__dict__:
                func = getattr(Sketch, name, None)
                if func is not None:
                    setattr(cls, name, func)

    # --- Lifecycle hooks (override in subclasses) ---
    def setup(self) -> None:
        """Called once before the run loop. Override in sketches."""
        return None

    def update(self, dt: float) -> None:
        """Called each frame before draw(); dt is time in seconds since last frame."""
        return None

    def draw(self) -> None:
        """Called each frame to perform drawing. Override in sketches."""
        return None

    def on_event(self, event: input_mod.Event) -> None:
        """Called for each pygame event after normalization. Override in sketches."""
        return None

    def teardown(self) -> None:
        """Called once when the run loop exits. Override to clean up resources."""
        return None

    def set_save_folder(self, folder: Optional[str]) -> None:
        """Set a per-sketch snapshots folder.

        Example:
            self.set_save_folder('snapshots')

        This preferred per-sketch value will be used by `save_snapshot()` when
        resolving relative paths. Use `None` to clear and fall back to the
        environment variable (if present) or the sketch directory.
        """
        self._save_folder = None if folder is None else str(folder)

    def size(self, w: int, h: int, fullscreen: bool = False) -> None:
        """Set the sketch window size. Call this in `setup()`.

        Args:
            w: width in pixels
            h: height in pixels
            fullscreen: whether to use fullscreen mode
        """
        self.width = int(w)
        self.height = int(h)
        self.fullscreen = bool(fullscreen)

    @property
    def save_folder(self) -> Optional[str]:
        """Property alias for the per-sketch snapshots folder.

        You can set this directly in a sketch: `self.save_folder = 'shots'`.
        """
        return self._save_folder

    @save_folder.setter
    def save_folder(self, folder: Optional[str]) -> None:
        self.set_save_folder(folder)

    # NOTE: `mouse_x` / `mouse_y` properties are defined later using
    # `mouse_pos()` which queries pygame. We keep internal `_mouse_x/_mouse_y`
    # for the input system but avoid duplicating property names here.

    def set_title(self, title: str) -> None:
        self._title = str(title)
        if pygame.display.get_init():
            pygame.display.set_caption(self._title)

    def no_cursor(self) -> None:
        """Hide the system mouse cursor for the sketch window.

        If called before the display exists, the request is recorded and
        applied when the window is created (similar to other pending state).
        """
        # Apply immediately if possible
        try:
            if pygame.display.get_init():
                pygame.mouse.set_visible(False)
                # Clear any pending sentinel
                self._pending_cursor = _PENDING_UNSET
                return
        except Exception:
            # ignore failures; fall back to pending behavior
            pass

        # Record pending request to hide cursor
        self._pending_cursor = False

    def cursor(self, visible: bool = True) -> None:
        """Show or hide the mouse cursor. Use `cursor(False)` to hide, or
        `cursor(True)` to show. Prefer `no_cursor()` for the hide case.
        """
        try:
            if pygame.display.get_init():
                pygame.mouse.set_visible(bool(visible))
                self._pending_cursor = _PENDING_UNSET
                return
        except Exception:
            pass

        self._pending_cursor = bool(visible)

    def background(self, *args) -> None:
        """Fill the entire canvas with a color. Accepts the same flexible
        forms as `fill()` and Processing.background():

          - background(r, g, b)
          - background(r, g, b, a)
          - background((r, g, b))
          - background((r, g, b, a))
          - background(ColorInstance)

        When called before a Surface exists the normalized value is recorded
        as pending and applied when the display is created.
        """
        # normalize into a single color-like object or None
        if len(args) == 0:
            # no-op when called without args (preserve prior behavior)
            return None

        if len(args) == 1:
            color_in = args[0]
        else:
            color_in = tuple(args)

        # If a Surface exists, try to apply immediately using surface.clear
        if self.surface is not None:
            try:
                # prefer surface.clear which understands color modes/alpha
                self.surface.clear(color_in)
                self._pending_background = _PENDING_UNSET
                return None
            except Exception:
                # fall through to record pending raw value
                pass

        # record pending background to apply later in run()
        self._pending_background = color_in
        return None

    # --- Transform helpers (delegate to active Surface when available) ---
    def push(self) -> None:
        """Push the current transform on the stack."""
        if self.surface is None:
            return
        try:
            self.surface.push()
        except Exception:
            pass

    # Processing-style alias
    def push_matrix(self) -> None:
        """Alias for push() to match Processing-style API."""
        return self.push()

    def pop(self) -> None:
        """Pop the top transform from the stack."""
        if self.surface is None:
            return
        try:
            self.surface.pop()
        except Exception:
            pass

    # Processing-style alias
    def pop_matrix(self) -> None:
        """Alias for pop() to match Processing-style API."""
        return self.pop()

    def translate(self, dx: float, dy: float) -> None:
        """Apply a translation to the current transform."""
        if self.surface is None:
            return
        try:
            self.surface.translate(dx, dy)
        except Exception:
            pass

    def rotate(self, theta: float) -> None:
        """Apply a rotation (radians) to the current transform."""
        if self.surface is None:
            return
        try:
            self.surface.rotate(theta)
        except Exception:
            pass

    def scale(self, sx: float, sy: float | None = None) -> None:
        """Apply a scale to the current transform."""
        if self.surface is None:
            return
        try:
            self.surface.scale(sx, sy)
        except Exception:
            pass

    def reset_matrix(self) -> None:
        """Reset the current transform matrix to identity."""
        if self.surface is None:
            return
        try:
            self.surface.reset_matrix()
        except Exception:
            pass

    def get_matrix(self) -> list[list[float]] | None:
        """Return a copy of the current transform matrix from the active surface, or None."""
        if self.surface is None:
            return None
        try:
            return self.surface.get_matrix()
        except Exception:
            return None

    def set_matrix(self, M: list[list[float]]) -> None:
        """Overwrite the current top matrix on the active surface with M."""
        if self.surface is None:
            return
        try:
            self.surface.set_matrix(M)
        except Exception:
            pass

    def transform(self, translate: tuple[float, float] | None = None, rotate: float | None = None, scale: tuple[float, float] | None = None):
        """Context manager that pushes a transform, applies optional ops, and pops on exit.

        Example:
            with self.transform(translate=(10,20), rotate=0.3):
                self.rect(...)
        """
        if self.surface is None:
            # no-op context manager
            from contextlib import contextmanager

            @contextmanager
            def _noop():
                yield None

            return _noop()
        return self.surface.transform(translate=translate, rotate=rotate, scale=scale)

    def set_double_buffer(self, enabled: bool) -> None:
        """Enable or disable double buffering for the display window.

        This will include the DOUBLEBUF flag when creating the pygame display.
        """
        self._double_buffer = bool(enabled)

    def set_vsync(self, vsync: int) -> None:
        """Request vsync behaviour on the display. Use 1 to enable, 0 to disable.

        Note: actual vsync support depends on the underlying SDL/pygame build.
        """
        try:
            self._vsync = int(vsync)
        except Exception:
            self._vsync = 0

    def frame_rate(self, fps: int) -> None:
        self._frame_rate = int(fps)

    def set_escape_closes(self, enabled: bool) -> None:
        """Enable or disable the default Escape-to-close behavior.

        By default the sketch will stop running when the user presses Escape.
        Call `self.set_escape_closes(False)` inside `setup()` to opt-out.
        """
        try:
            self._escape_closes = bool(enabled)
        except Exception:
            self._escape_closes = True

    # --- Surface state helpers (delegate to self.surface) ---
    def fill(self, *args):
        """Set the sketch fill color.

        Accepts the same flexible forms as `Surface.fill` and `Surface._coerce_input_color`:
          - fill(r, g, b)
          - fill(r, g, b, a)
          - fill((r, g, b))
          - fill((r, g, b, a))
          - fill(None)  # disable fill

        When called before the Surface exists the normalized args are
        recorded as pending and applied in `run()` (same behavior as other
        pending state helpers).
        """
        # Normalize incoming args into a single color object or None
        if len(args) == 0:
            # no-op / getter not supported on Sketch wrapper; keep prior behavior
            return None

        if len(args) == 1:
            color_in = args[0]
        else:
            # multiple positional args -> treat as individual channels
            color_in = tuple(args)

        # If explicit None provided, treat as no_fill()
        if color_in is None:
            if self.surface is not None:
                try:
                    self.surface.no_fill()
                    return None
                except Exception:
                    self._pending_fill = None
                    return None
            else:
                self._pending_fill = None
                return None

        # If a surface exists, attempt to coerce & apply immediately
        if self.surface is not None:
            try:
                coerced = self.surface._coerce_input_color(color_in)
                # Surface._fill expects a ColorTupleOrNone; cast the result
                self.surface._fill = cast(ColorTupleOrNone, tuple(coerced)) if coerced is not None else None
                return None
            except Exception:
                # fallback: try calling surface.fill directly
                try:
                    self.surface.fill(color_in)
                    return None
                except Exception:
                    # record pending raw value as a last resort
                    self._pending_fill = color_in
                    return None

        # Surface not yet available: record pending raw value
        self._pending_fill = color_in
        return None

    def no_fill(self) -> None:
        if self.surface is not None:
            self.surface.no_fill()
        else:
            self._pending_fill = None

    def stroke(self, *args):
        """Set the sketch stroke color. Accepts the same flexible forms as fill():

          - stroke(r, g, b)
          - stroke(r, g, b, a)
          - stroke((r, g, b))
          - stroke((r, g, b, a))
          - stroke(None)  # disable stroke
        """
        # Normalize incoming args into a single color object or None
        if len(args) == 0:
            # no-op / getter not supported on Sketch wrapper
            return None

        if len(args) == 1:
            color_in = args[0]
        else:
            color_in = tuple(args)

        # If explicit None provided, treat as no_stroke()
        if color_in is None:
            if self.surface is not None:
                try:
                    self.surface.no_stroke()
                    return None
                except Exception:
                    self._pending_stroke = None
                    return None
            else:
                self._pending_stroke = None
                return None

        # If a surface exists, attempt to coerce & apply immediately
        if self.surface is not None:
            try:
                coerced = self.surface._coerce_input_color(color_in)
                # Surface._stroke expects a ColorTupleOrNone; cast the result
                self.surface._stroke = cast(ColorTupleOrNone, tuple(coerced)) if coerced is not None else None
                return None
            except Exception:
                # fallback: try calling surface.stroke directly
                try:
                    self.surface.stroke(color_in)
                    return None
                except Exception:
                    self._pending_stroke = color_in
                    return None

        # Surface not yet available: record pending raw value
        self._pending_stroke = color_in
        return None

    def no_stroke(self) -> None:
        if self.surface is not None:
            self.surface.no_stroke()
        else:
            self._pending_stroke = None

    def stroke_weight(self, w: int) -> None:
        if self.surface is not None:
            self.surface.stroke_weight(w)
        else:
            self._pending_stroke_weight = int(w)

    def rect_mode(self, mode: Optional[str] = None) -> str | None:
        """Get or set rectangle mode. When called before a Surface exists this
        records a pending value which will be applied when the display is
        created (in `run()`).
        """
        if self.surface is not None:
            return self.surface.rect_mode(mode)
        # when called with no args, return the pending or default
        if mode is None:
            v = self._pending_rect_mode
            if v is _PENDING_UNSET:
                return None
            return cast(str, v)
        try:
            m = str(mode).upper()
        except Exception:
            return None
        if m in (GraphicsSurface.MODE_CORNER, GraphicsSurface.MODE_CENTER):
            self._pending_rect_mode = m
        return None

    def ellipse_mode(self, mode: Optional[str] = None) -> str | None:
        """Get or set ellipse mode. When called before a Surface exists this
        records a pending value which will be applied when the display is
        created (in `run()`).
        """
        if self.surface is not None:
            return self.surface.ellipse_mode(mode)
        if mode is None:
            v = self._pending_ellipse_mode
            if v is _PENDING_UNSET:
                return None
            return cast(str, v)
        try:
            m = str(mode).upper()
        except Exception:
            return None
        if m in (GraphicsSurface.MODE_CORNER, GraphicsSurface.MODE_CENTER):
            self._pending_ellipse_mode = m
        return None

    def image_mode(self, mode: Optional[str] = None) -> str | None:
        """Get or set image mode. When called before a Surface exists this
        records a pending value which will be applied when the display is
        created (in `run()`)."""
        if self.surface is not None:
            return self.surface.image_mode(mode)
        if mode is None:
            v = self._pending_image_mode
            if v is _PENDING_UNSET:
                return None
            return cast(str, v)
        try:
            m = str(mode).upper()
        except Exception:
            return None
        if m in (GraphicsSurface.MODE_CORNER, GraphicsSurface.MODE_CENTER, GraphicsSurface.MODE_CORNERS):
            self._pending_image_mode = m
        return None

    def tint(self, *args):
        """Get or set the tint color. Accepts the same overloads as Surface.tint.

        If called before a Surface exists the raw args are recorded and coerced
        when the Surface is created.
        """
        if len(args) == 0:
            if self.surface is not None:
                return self.surface.tint()
            return self._pending_tint if self._pending_tint is not _PENDING_UNSET else None

        # store pending raw args; coercion happens in initialize when applying pending state
        if self.surface is not None:
            try:
                self.surface.tint(*args)
                return None
            except Exception:
                self._pending_tint = args
                return None
        else:
            self._pending_tint = args
            return None

    def blend_mode(self, mode: Optional[str] = None) -> str | None:
        """Get or set blend mode on the active surface (or record pending).

        When called before a Surface exists this records the pending mode and
        applies it when the Surface is created. When the surface exists this
        forwards to `Surface.blend_mode()`.
        """
        if self.surface is not None:
            return self.surface.blend_mode(mode)
        # getter when no surface
        if mode is None:
            v = self._pending_blend
            if v is _PENDING_UNSET:
                return None
            return cast(str, v)
        try:
            m = str(mode)
        except Exception:
            return None
        # record pending value for later application
        self._pending_blend = m
        return None

    def color_mode(self, mode: Optional[str] = None, max1: int = 255, max2: int = 255, max3: int = 255, max4: int | None = None):
        """Get or set color mode. When called before a Surface exists this
        records a pending color_mode tuple which will be applied in run().
        """
        if self.surface is not None:
            # forward optional alpha max when surface exists
            return self.surface.color_mode(mode, max1, max2, max3, max4)
        if mode is None:
            v = self._pending_color_mode
            if v is _PENDING_UNSET:
                return None
            return cast(tuple, v)
        try:
            m = str(mode).upper()
            if m in ("RGB", "HSB"):
                # store optional fourth max (alpha) as well for parity with Processing
                a_max = int(max4) if max4 is not None else int(max1)
                self._pending_color_mode = (m, int(max1), int(max2), int(max3), a_max)
        except Exception:
            pass
        return None

    def text(self, txt: str, x: int, y: int, font_name: Optional[str] = None, size: int = 24, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        if self.surface is not None:
            self.surface.text(txt, x, y, font_name=font_name, size=size, color=color)

    def point(self, x: float, y: float, color: Optional[Tuple[int, int, int]] = None, z: float | None = None) -> None:
        """Draw a point on the sketch surface. Delegates to Surface.point.

        If `color` is provided it will be coerced; otherwise the surface's
        current stroke color is used. If the surface is not yet available
        the call is ignored (consistent with other drawing helpers).
        """
        if self.surface is None:
            return
        if color is not None:
            try:
                from typing import cast
                from .color import Color
                coerced = self.surface._coerce_input_color(color)
                # coerced may be a Color-like object with to_tuple(), or an
                # iterable/tuple. Normalize to a concrete tuple form expected
                # by Surface.point. Use isinstance() to narrow for the static
                # type checker instead of hasattr checks.
                if isinstance(coerced, Color):
                    candidate = coerced.to_tuple()
                elif isinstance(coerced, tuple):
                    candidate = tuple(coerced)  # already a concrete tuple
                elif coerced is None:
                    candidate = None
                else:
                    try:
                        if isinstance(coerced, Iterable) and not isinstance(coerced, (str, bytes, bytearray)):
                            candidate = tuple(coerced)
                        else:
                            candidate = None
                    except Exception:
                        candidate = None
                # cast to the narrow union the Surface.point accepts
                col_tuple = cast(tuple | None, candidate)
                self.surface.point(x, y, col_tuple, z)
                return
            except Exception:
                # best-effort: fall back to passing the raw color through
                try:
                    self.surface.point(x, y, color, z)
                    return
                except Exception:
                    return
        # no explicit color: let the surface use its current stroke
        try:
            self.surface.point(x, y, None, z)
        except Exception:
            return

    # --- color/channel helpers (convenience for sketches) ---
    def _coerce_color(self, c):
        """Coerce various color forms to a Color instance.

        Accepts a Color instance, a tuple/list (r,g,b) or (r,g,b,a), or an
        OffscreenSurface.get() return value. Returns a Color instance.
        """
        from .color import Color as _Color

        if isinstance(c, _Color):
            return c
        try:
            # tuple or list
            if hasattr(c, "__iter__"):
                vals = list(c)
                if len(vals) == 4:
                    return _Color.from_rgb(vals[0], vals[1], vals[2], vals[3])
                elif len(vals) == 3:
                    return _Color.from_rgb(vals[0], vals[1], vals[2])
        except Exception:
            pass
        # fallback black
        return _Color.from_rgb(0, 0, 0)

    def red(self, c) -> int:
        return int(self._coerce_color(c).r)

    def green(self, c) -> int:
        return int(self._coerce_color(c).g)

    def blue(self, c) -> int:
        return int(self._coerce_color(c).b)

    def alpha(self, c) -> int:
        return int(self._coerce_color(c).a)

    def hue(self, c) -> int:
        col = self._coerce_color(c)
        # use current color_mode to determine scaling; default to 255
        cm = self.color_mode() or ("RGB", 255, 255, 255)
        if isinstance(cm, tuple) and len(cm) >= 2 and cm[0] == "HSB":
            max_h = cm[1]
        else:
            max_h = 255
        h, s, v, a = col.to_hsb(max_h=max_h)
        return int(h)

    def saturation(self, c) -> int:
        col = self._coerce_color(c)
        cm = self.color_mode() or ("RGB", 255, 255, 255)
        max_s = cm[2] if isinstance(cm, tuple) and len(cm) >= 3 else 255
        max_h_for_call = cm[1] if isinstance(cm, tuple) and len(cm) >= 2 else 255
        h, s, v, a = col.to_hsb(max_h=max_h_for_call, max_s=max_s)
        return int(s)

    def brightness(self, c) -> int:
        col = self._coerce_color(c)
        cm = self.color_mode() or ("RGB", 255, 255, 255)
        max_v = cm[3] if isinstance(cm, tuple) and len(cm) >= 4 else 255
        max_h_for_call = cm[1] if isinstance(cm, tuple) and len(cm) >= 2 else 255
        h, s, v, a = col.to_hsb(max_h=max_h_for_call, max_v=max_v)
        return int(v)

    def load_image(self, path: str) -> object:
        """Load an image using the Assets manager if available.

        The Assets manager searches sketch/data and the sketch directory and caches images.
        """
        # prefer assets manager which handles resolution and caching
        try:
            if hasattr(self, "assets") and self.assets:
                img = self.assets.load_image(path)
                if img is not None:
                    return OffscreenSurface(cast(pygame.Surface, getattr(img, "raw", img)))
        except Exception as e:
            print(f"Sketch: Assets.load_image failed for '{path}': {e}")

        # fallback to surface loader if available
        try:
            if self.surface is not None:
                loader = getattr(self.surface, "load_image", None)
                if callable(loader):
                    img = loader(path)
                    if img is not None:
                        return OffscreenSurface(cast(pygame.Surface, getattr(img, "raw", img)))
        except Exception:
            pass

        # final fallback to pygame
        try:
            img = pygame.image.load(path)
            return OffscreenSurface(cast(pygame.Surface, img))
        except Exception:
            print(f"Failed to load image: {path}")
            return None

    def load_shape(self, path: str):
        """Load a vector shape (SVG/OBJ) via the Assets manager or by resolving path.

        Returns a PShape-like object or None on failure.
        """
        # Prefer the instantiated assets manager when available
        try:
            if hasattr(self, "assets") and self.assets:
                shp = self.assets.load_shape(path)
                if shp is not None:
                    return shp
        except Exception:
            # best-effort: continue to fallback loaders
            pass

        # Fallback: attempt to resolve relative to sketch path (no assets manager)
        try:
            base = os.path.dirname(self.sketch_path) if self.sketch_path else os.getcwd()
            tmp = Assets(base)
            shp = tmp.load_shape(path)
            return shp
        except Exception:
            return None

    def blit_image(self, img: object, x: int = 0, y: int = 0) -> None:
        if self.surface is not None and img is not None:
            self.surface.blit_image(img, x=x, y=y)

    # --- Backwards-compatible primitive wrappers (old example APIs) ---
    def line(self, x1, y1, x2, y2, stroke: ColorTupleOrNone = None, stroke_width: Optional[int] = None, cap: Optional[str] = None, join: Optional[str] = None):
        if self.surface is None:
            return
        # If stroke/stroke_width are None, Surface.line will use the global
        # stroke/stroke_weight state.
        self.surface.line(x1, y1, x2, y2, color=stroke, width=stroke_width, cap=cap, join=join)

    def rect(self, x, y, w, h, fill=None, stroke=None, stroke_width=None):
        if self.surface is None:
            return
        # forward per-call styles to Surface.rect
        self.surface.rect(x, y, w, h, fill=fill, stroke=stroke, stroke_weight=stroke_width)

    def triangle(self, x1, y1, x2, y2, x3, y3, fill: ColorTupleOrNone = None, stroke: ColorTupleOrNone = None, stroke_width: Optional[int] = None):
        if self.surface is None:
            return
        pts = [(x1, y1), (x2, y2), (x3, y3)]
        # forward per-call styles to Surface.polygon_with_style
        self.surface.polygon_with_style(pts, fill=fill, stroke=stroke, stroke_weight=stroke_width)

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4, fill: ColorTupleOrNone = None, stroke: ColorTupleOrNone = None, stroke_width: Optional[int] = None):
        if self.surface is None:
            return
        pts = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        # forward per-call styles to Surface.polygon_with_style for parity
        # with other shape helpers.
        self.surface.polygon_with_style(pts, fill=fill, stroke=stroke, stroke_weight=stroke_width)

    def polyline(self, points: list[tuple[float, float]], stroke: ColorTupleOrNone = None, stroke_width: Optional[int] = None):
        """Draw an open polyline. Accepts list of (x,y) points and optional stroke/stroke_width.

        This temporarily applies stroke settings like other compatibility shims.
        """
        if self.surface is None:
            return
        # forward per-call styles to Surface.polyline_with_style
        self.surface.polyline_with_style(points, stroke=stroke, stroke_weight=stroke_width)

    # --- Shape construction wrappers (begin_shape/vertex/end_shape) ---
    def begin_shape(self, mode: str | None = None) -> None:
        """Begin constructing a custom shape. Delegates to the active Surface."""
        if self.surface is not None:
            self.surface.begin_shape(mode)

    def vertex(self, x: float, y: float) -> None:
        """Add a vertex to the currently constructed shape."""
        if self.surface is not None:
            self.surface.vertex(x, y)

    def bezier_vertex(self, cx1: float, cy1: float, cx2: float, cy2: float, x3: float, y3: float) -> None:
        """Add a cubic bezier vertex segment to the current shape."""
        if self.surface is not None:
            self.surface.bezier_vertex(cx1, cy1, cx2, cy2, x3, y3)

    # Processing-style alias
    bezierVertex = bezier_vertex

    def end_shape(self, close: bool = False) -> None:
        """Finish the current shape and draw it. Delegates to the active Surface."""
        if self.surface is not None:
            self.surface.end_shape(close=close)

    def bezier(self, x1: float, y1: float, cx1: float, cy1: float, cx2: float, cy2: float, x2: float, y2: float) -> None:
        """Draw a cubic bezier curve. Delegates to the active surface.

        Signature matches Processing's `bezier(x1,y1,cx1,cy1,cx2,cy2,x2,y2)`.
        """
        if self.surface is None:
            return
        self.surface.bezier(x1, y1, cx1, cy1, cx2, cy2, x2, y2)

    def bezier_detail(self, steps: int) -> None:
        """Set bezier sampling detail on the active surface."""
        if self.surface is None:
            return
        self.surface.bezier_detail(steps)

    def arc(self, x, y, w, h, start_rad, end_rad, mode="open", fill=None, stroke=None, stroke_width=None):
        if self.surface is None:
            return
        # prefer stroke_width alias
        if stroke_width is not None:
            self.surface.stroke_weight(int(stroke_width))
        # forward to Surface.arc; Surface.arc will accept per-call styles
        self.surface.arc(x, y, w, h, start_rad, end_rad, mode=mode, fill=fill, stroke=stroke)

    def image(self, img, x, y, w=None, h=None):
        if self.surface is None or img is None:
            return
        src = getattr(img, "raw", img)
        if w is None or h is None:
            self.surface.blit_image(src, int(x), int(y))
            return
        # scale image using the underlying surface
        scaled = pygame.transform.smoothscale(src, (int(w), int(h)))
        self.surface.blit_image(scaled, int(x), int(y))

    def shape_mode(self, mode: str | None) -> None:
        """Set the current shape drawing mode used by `shape()`.

        mode may be one of: None (default, CORNER), 'CORNER', 'CORNERS', 'CENTER'.
        """
        # If a surface exists, set directly, otherwise record pending value
        if self.surface is not None:
            try:
                setter = getattr(self.surface, "set_shape_mode", None)
                if callable(setter):
                    setter(mode)
                    return
            except Exception:
                pass
        # record pending for when surface is created
        self._pending_shape_mode = mode

    def shape(self, shp, x: float, y: float, w: Optional[float] = None, h: Optional[float] = None) -> None:
        """Draw a loaded PShape-like object at the requested location/size.

        This delegates to the active Surface.shape implementation and respects
        the current `shape_mode` set via `shape_mode()`.
        """
        if self.surface is None or shp is None:
            return
        # ensure surface has the pending shape mode applied
        if getattr(self, "_pending_shape_mode", None) is not None:
            try:
                setter = getattr(self.surface, "set_shape_mode", None)
                if callable(setter):
                    setter(self._pending_shape_mode)
            except Exception:
                pass
            self._pending_shape_mode = None
        try:
            drawer = getattr(self.surface, "shape", None)
            if callable(drawer):
                drawer(shp, x, y, w, h)
        except Exception:
            pass

    def style(self, *args, **kwargs):
        """Return a context manager that temporarily overrides drawing style on the active surface.

        Example:
            with self.style(fill=None):
                self.rect(10,10,100,100)
        """
        if self.surface is None:
            # no-op context manager
            from contextlib import contextmanager

            @contextmanager
            def _noop():
                yield None

            return _noop()
        return self.surface.style(*args, **kwargs)

    # --- PImage-style convenience wrappers ---
    def get(self, *args):
        if self.surface is None:
            raise RuntimeError("No surface available")
        return self.surface.get(*args)

    def copy(self, *args):
        if self.surface is None:
            raise RuntimeError("No surface available")
        return self.surface.copy(*args)

    def set(self, x, y, value):
        if self.surface is None:
            raise RuntimeError("No surface available")
        return self.surface.set(x, y, value)

    def save_frame(self, path: str) -> None:
        """Save the current main surface to disk.

        This helper exists so sketches don't need to `import pygame` themselves
        just to save a PNG frame. It's best-effort and will not raise on
        failure (keeps examples convenient).
        """
        if self.surface is None:
            return
        try:
            # If a relative path is provided, save relative to the sketch file
            # so examples that call `self.save_snapshot('out.png')` end up next
            # to the sketch instead of the project root.
            # Prefer a per-sketch configured directory (`self.save_folder`) if set;
            # otherwise fall back to the `PYCREATIVE_SNAP_DIR` environment variable.
            snapshots_dir = self._save_folder if self._save_folder is not None else os.getenv("PYCREATIVE_SNAP_DIR")

            target = path
            if not os.path.isabs(target):
                base_dir = os.path.dirname(self.sketch_path) if self.sketch_path else os.getcwd()
                if snapshots_dir:
                    # snapshots_dir may be relative to sketch dir
                    if not os.path.isabs(snapshots_dir):
                        snapshots_dir = os.path.join(base_dir, snapshots_dir)
                    # ensure snapshots dir exists
                    try:
                        os.makedirs(snapshots_dir, exist_ok=True)
                    except Exception:
                        pass
                    target = os.path.join(snapshots_dir, target)
                else:
                    target = os.path.join(base_dir, target)

            # Support sequential numbering for contiguous sequences.
            # Patterns supported:
            #  - filename_{n}.png  -> will replace {n} with next integer
            #  - filename_###.png   -> will replace ### with zero-padded next int
            # If no pattern is present, we leave the name as-is.
            def _next_sequence_name(path_template: str) -> str:
                dirname, fname = os.path.split(path_template)
                name, ext = os.path.splitext(fname)
                # {n} style
                if "{n}" in name:
                    # find existing matches and pick next
                    i = 1
                    while True:
                        candidate = name.replace("{n}", str(i)) + ext
                        cand_path = os.path.join(dirname, candidate)
                        if not os.path.exists(cand_path):
                            return cand_path
                        i += 1
                # #### style: sequence of # characters
                hashes = None
                for seq in ["#" * k for k in range(6, 0, -1)]:
                    if seq in name:
                        hashes = seq
                        break
                if hashes:
                    pad = len(hashes)
                    base = name.replace(hashes, "{}")
                    i = 1
                    while True:
                        candidate = (base.format(str(i).zfill(pad))) + ext
                        cand_path = os.path.join(dirname, candidate)
                        if not os.path.exists(cand_path):
                            return cand_path
                        i += 1
                # otherwise, return as-is
                return path_template

            target = _next_sequence_name(target)

            # ensure directory exists when a directory component is provided
            d = os.path.dirname(target)
            if d:
                try:
                    os.makedirs(d, exist_ok=True)
                except Exception:
                    # ignore directory creation errors; we'll attempt save anyway
                    pass

            pygame.image.save(self.surface.raw, target)
        except Exception as e:
            # best-effort; don't raise from examples, but include useful debug info
            import traceback

            print(f"Failed to save snapshot to {path}: {e}")
            traceback.print_exc()

    # NOTE: no alias for save_snapshot; use `save_frame()`

    # (math wrappers defined later)
    def constrain(self, val, minimum, maximum):
        """Constrain a value to lie between minimum and maximum (inclusive).

        Mirrors Processing.constrain(): returns `minimum` if `val < minimum`,
        `maximum` if `val > maximum`, otherwise returns `val`.

        Works with ints and floats and will attempt to coerce numeric-like inputs.
        """
        try:
            v = float(val)
            lo = float(minimum)
            hi = float(maximum)
            # If min > max, behave like Processing and swap them
            if lo > hi:
                lo, hi = hi, lo
            if v < lo:
                return int(lo) if isinstance(val, int) and lo.is_integer() else lo
            if v > hi:
                return int(hi) if isinstance(val, int) and hi.is_integer() else hi
            # return same type as input when reasonable
            if isinstance(val, int) and v.is_integer():
                return int(v)
            return v
        except Exception:
            # best-effort fallback: return val unchanged on failure
            return val

    def dist(self, x1: float, y1: float, x2: float, y2: float) -> float:
        """Return the Euclidean distance between two 2D points.

        Mirrors Processing.dist(x1, y1, x2, y2).
        """
        try:
            import math

            return float(math.hypot(float(x2) - float(x1), float(y2) - float(y1)))
        except Exception:
            # best-effort: attempt numeric subtraction or fallback to 0.0
            try:
                dx = float(x2) - float(x1)
                dy = float(y2) - float(y1)
                return float((dx * dx + dy * dy) ** 0.5)
            except Exception:
                return 0.0

    def color(self, *args):
        """Create a Color object like Processing's color().

        Behavior:
        - If current color_mode is HSB, interprets args as (h,s,v) or (h,s,v,a)
        - If current color_mode is RGB, interprets args as (r,g,b) or (r,g,b,a)
        Returns a `Color` instance.
        """
        # lazy import to avoid heavy deps at module import time
        from .color import Color

        # determine active color mode and ranges (use pending if surface not yet created)
        cm = None
        if self.surface is not None:
            cm = self.surface.color_mode()
        else:
            cm = self._pending_color_mode if self._pending_color_mode is not _PENDING_UNSET else None

        if cm is None:
            # default to RGB 0-255
            mode, m1, m2, m3 = ("RGB", 255, 255, 255)
            m4 = 255
        else:
            try:
                # pending color mode may include a 4th alpha max value
                if isinstance(cm, tuple) and len(cm) == 5:
                    mode, m1, m2, m3, m4 = cm
                else:
                    mode, m1, m2, m3 = cm
                    m4 = m1
            except Exception:
                mode, m1, m2, m3 = ("RGB", 255, 255, 255)
                m4 = 255

        # support HSB or RGB
        if str(mode).upper() == "HSB":
            # expect (h,s,v) or (h,s,v,a)
            h = args[0] if len(args) > 0 else 0
            s = args[1] if len(args) > 1 else 0
            v = args[2] if len(args) > 2 else 0
            # If an alpha was provided as the 4th positional arg, pass it through.
            if len(args) >= 4:
                a = args[3]
                c = Color.from_hsb(float(h), float(s), float(v), a=a, max_h=int(m1), max_s=int(m2), max_v=int(m3), max_a=int(m4))
            else:
                c = Color.from_hsb(float(h), float(s), float(v), max_h=int(m1), max_s=int(m2), max_v=int(m3), max_a=int(m4))
            return c

        # default: RGB
        r = args[0] if len(args) > 0 else 0
        g = args[1] if len(args) > 1 else 0
        b = args[2] if len(args) > 2 else 0
        if len(args) >= 4:
            a = args[3]
            try:
                c = Color.from_rgb(r, g, b, a=a, max_value=int(m1))
            except TypeError:
                # fallback for older signatures: construct and set alpha
                c = Color.from_rgb(r, g, b, max_value=int(m1))
                try:
                    c.a = int(a) & 255
                except Exception:
                    pass
        else:
            c = Color.from_rgb(r, g, b, max_value=int(m1))
        return c

    def lerp_color(self, c1, c2, amt: float):
        """Interpolate between two colors and return a `pycreative.color.Color`.

        `amt` in [0,1]. Interpolation happens in the current color_mode (HSB or RGB).
        Inputs may be `Color` instances or tuples (3- or 4-length). The returned
        value is a `Color` instance.
        """
        from .color import Color
        import colorsys

        def to_color(x):
            if isinstance(x, Color):
                return x
            if hasattr(x, "__iter__"):
                vals = list(x)
                # fallback: interpret using current color() helper semantics
                return self.color(*vals)
            # last resort: treat as grayscale
            return Color.from_rgb(x, x, x)

        a = max(0.0, min(1.0, float(amt)))
        col1 = to_color(c1)
        col2 = to_color(c2)

        # determine mode and ranges
        cm = None
        if self.surface is not None:
            cm = self.surface.color_mode()
        else:
            cm = self._pending_color_mode if self._pending_color_mode is not _PENDING_UNSET else None

        if cm is None:
            mode, m1, m2, m3 = ("RGB", 255, 255, 255)
        else:
            try:
                # color_mode may include an optional alpha max as a 5th element;
                # we only need the first four values here (mode, m1, m2, m3).
                mode = cm[0]
                m1 = int(cm[1])
                m2 = int(cm[2])
                m3 = int(cm[3])
            except Exception:
                mode, m1, m2, m3 = ("RGB", 255, 255, 255)

        if str(mode).upper() == "HSB":
            # convert RGB to normalized HSV via colorsys (expects 0..1)
            r1, g1, b1 = col1.r / 255.0, col1.g / 255.0, col1.b / 255.0
            r2, g2, b2 = col2.r / 255.0, col2.g / 255.0, col2.b / 255.0
            h1, s1, v1 = colorsys.rgb_to_hsv(r1, g1, b1)
            h2, s2, v2 = colorsys.rgb_to_hsv(r2, g2, b2)
            # h is 0..1; linear interpolate (no shortest-hue wrap handling)
            h = (h1 + (h2 - h1) * a) % 1.0
            s = s1 + (s2 - s1) * a
            v = v1 + (v2 - v1) * a
            # scale to Processing-style ranges when calling from_hsb
            H = h * float(int(m1))
            S = s * float(int(m2))
            V = v * float(int(m3))
            out = Color.from_hsb(H, S, V, max_h=int(m1), max_s=int(m2), max_v=int(m3))
        else:
            # RGB linear interpolation
            r = int(round(col1.r + (col2.r - col1.r) * a))
            g = int(round(col1.g + (col2.g - col1.g) * a))
            b = int(round(col1.b + (col2.b - col1.b) * a))
            out = Color(r, g, b)

        # interpolate alpha
        try:
            a1 = getattr(col1, "a", 255)
            a2 = getattr(col2, "a", 255)
            out.a = int(round(a1 + (a2 - a1) * a)) & 255
        except Exception:
            out.a = 255

        return out

    def random(self, *args) -> float:
        """Return a random float similar to Processing.random().

        Usage:
          self.random() -> float in [0,1)
          self.random(high) -> float in [0, high)
          self.random(low, high) -> float in [low, high)
        """
        import random as _random

        try:
            if len(args) == 0:
                return _random.random()
            if len(args) == 1:
                high = float(args[0])
                return _random.random() * high
            if len(args) >= 2:
                low = float(args[0])
                high = float(args[1])
                return low + _random.random() * (high - low)
        except Exception:
            return 0.0
        # fallback
        return 0.0

    def random_gaussian(self) -> float:
        """Return a normally-distributed random number with mean 0 and stddev 1.

        This mirrors Processing.randomGaussian(). For reproducible results
        use `self.random_seed()` which seeds Python's `random` module.
        """
        import random as _random

        try:
            return _random.gauss(0.0, 1.0)
        except Exception:
            # fallback: use Box-Muller directly
            try:
                u1 = _random.random()
                u2 = _random.random()
                import math

                z0 = math.sqrt(-2.0 * math.log(max(u1, 1e-12))) * math.cos(2.0 * math.pi * u2)
                return z0
            except Exception:
                return 0.0

    def random_seed(self, seed: int | None):
        """Seed the random number generator (Processing.randomSeed equivalent).

        Provide `None` to re-seed from the OS default.
        """
        import random as _random

        try:
            if seed is None:
                _random.seed()
            else:
                _random.seed(int(seed))
        except Exception:
            # best-effort, ignore invalid seeds
            try:
                _random.seed()
            except Exception:
                pass

    def stroke_width(self, w: int) -> None:
        if self.surface is not None:
            self.surface.stroke_weight(w)

    def _get_stroke_cap(self) -> Any:
        """Get or set the global stroke cap. Valid values: 'butt','round','square'.

        When set before a Surface exists the value is recorded and applied when
        the Surface is created. When a Surface exists it is applied immediately.
        """
        # Return a callable proxy so older sketches can call `self.stroke_cap('square')`
        # while newer code can do property assignment `self.stroke_cap = 'round'`.
        sketch = self

        class _CapProxy:
            def __call__(self, cap_val: str | None) -> None:
                sketch._apply_stroke_cap(cap_val)

            def __str__(self) -> str:
                if sketch.surface is not None:
                    return str(getattr(sketch.surface, "_line_cap", None))
                v = sketch._pending_line_cap
                return str(None if v is _PENDING_UNSET else v)

            def __repr__(self) -> str:
                return f"<stroke_cap {str(self)}>"

            def __eq__(self, other) -> bool:
                if sketch.surface is not None:
                    return getattr(sketch.surface, "_line_cap", None) == other
                v = sketch._pending_line_cap
                return (None if v is _PENDING_UNSET else v) == other

        return _CapProxy()

    def _apply_stroke_cap(self, cap: str | None) -> None:
        valid = ("butt", "round", "square")
        if cap is not None:
            c = str(cap)
            if c not in valid:
                raise ValueError(f"Invalid stroke cap: {cap}")
            cap = c

        if self.surface is not None:
            try:
                # delegate to Surface; when cap is None set default 'butt'
                if cap is None:
                    self.surface.set_line_cap("butt")
                else:
                    self.surface.set_line_cap(cap)
                # clear any pending sentinel
                self._pending_line_cap = _PENDING_UNSET
                return
            except Exception:
                # fallback to pending behavior
                pass

        # record pending value (None means clear)
        self._pending_line_cap = cap

    def _set_stroke_cap(self, cap: str | None) -> None:
        self._apply_stroke_cap(cap)

    # Explicit property to avoid confusing static analyzers with decorator-based
    # setter bindings on callables.
    stroke_cap = property(_get_stroke_cap, _set_stroke_cap)

    def _get_stroke_join(self) -> Any:
        """Get or set the global stroke join. Valid values: 'miter','round','bevel'."""
        # Return a callable proxy for backwards-compatible call-style usage
        sketch = self

        class _JoinProxy:
            def __call__(self, join_val: str | None) -> None:
                sketch._apply_stroke_join(join_val)

            def __str__(self) -> str:
                if sketch.surface is not None:
                    return str(getattr(sketch.surface, "_line_join", None))
                v = sketch._pending_line_join
                return str(None if v is _PENDING_UNSET else v)

            def __repr__(self) -> str:
                return f"<stroke_join {str(self)}>"

            def __eq__(self, other) -> bool:
                if sketch.surface is not None:
                    return getattr(sketch.surface, "_line_join", None) == other
                v = sketch._pending_line_join
                return (None if v is _PENDING_UNSET else v) == other

        return _JoinProxy()

    def _apply_stroke_join(self, join: str | None) -> None:
        valid = ("miter", "round", "bevel")
        if join is not None:
            j = str(join)
            if j not in valid:
                raise ValueError(f"Invalid stroke join: {join}")
            join = j

        if self.surface is not None:
            try:
                if join is None:
                    self.surface.set_line_join("miter")
                else:
                    self.surface.set_line_join(join)
                self._pending_line_join = _PENDING_UNSET
                return
            except Exception:
                pass

        self._pending_line_join = join

    def _set_stroke_join(self, join: str | None) -> None:
        self._apply_stroke_join(join)

    stroke_join = property(_get_stroke_join, _set_stroke_join)

    # --- Mouse helpers ---
    def mouse_pos(self) -> Optional[tuple[int, int]]:
        """Return the current mouse (x, y) position in window coordinates.

        This is a convenience wrapper around `pygame.mouse.get_pos()` and may
        return None if the underlying pygame mouse API is unavailable.
        """
        try:
            pos = pygame.mouse.get_pos()
            # pos may be a sequence-like (x,y)
            return (int(pos[0]), int(pos[1]))
        except Exception:
            return None

    @property
    def mouse_x(self) -> Optional[int]:
        """Return the current mouse x position or None if unavailable."""
        # Prefer the value updated by the input dispatch system if available
        mx = getattr(self, "_mouse_x", None)
        if mx is not None:
            try:
                return int(mx)
            except Exception:
                return None
        p = self.mouse_pos()
        return int(p[0]) if p is not None else None

    @property
    def mouse_y(self) -> Optional[int]:
        """Return the current mouse y position or None if unavailable."""
        my = getattr(self, "_mouse_y", None)
        if my is not None:
            try:
                return int(my)
            except Exception:
                return None
        p = self.mouse_pos()
        return int(p[1]) if p is not None else None

    # --- Basic drawing primitives ---
    def clear(self, *args) -> None:
        """Clear the canvas with a color. Accepts the same flexible forms as
        background()/fill():
          - clear(r, g, b)
          - clear(r, g, b, a)
          - clear((r,g,b))
          - clear(ColorInstance)
        If called when a surface exists this delegates to `Surface.clear()`.
        When no surface exists this is a no-op.
        """
        if len(args) == 0:
            return None
        if len(args) == 1:
            color_in = args[0]
        else:
            color_in = tuple(args)
        if self.surface is not None:
            try:
                self.surface.clear(color_in)
            except Exception:
                # best-effort: ignore
                pass
        return None

    def ellipse(
        self,
        x: float,
        y: float,
        w: float,
        h: float | None = None,
        fill: Optional[Tuple[int, int, int]] = None,
        stroke: Optional[Tuple[int, int, int]] = None,
        stroke_weight: Optional[int] = None,
        stroke_width: Optional[int] = None,
    ) -> None:
        """Draw an ellipse. Backwards-compatible parameters (fill/stroke/stroke_weight)
        are applied temporarily to the surface state if provided.
        """
        if self.surface is None:
            return

        # accept both stroke_weight and stroke_width for compatibility;
        # prefer stroke_width if provided by caller.
        chosen_sw = None
        if stroke_width is not None:
            chosen_sw = int(stroke_width)
        elif stroke_weight is not None:
            chosen_sw = int(stroke_weight)

        # treat the 3-argument form (x,y,d) like Processing: diameter used as both
        # width and height when `h` is omitted.
        hh = float(w) if h is None else float(h)

        # forward per-call styles to Surface.ellipse which will coerce
        # HSB/RGB tuples as needed and won't clear the surface
        try:
            self.surface.ellipse(x, y, float(w), hh, fill=fill, stroke=stroke, stroke_weight=chosen_sw)
        except Exception:
            # best-effort: ignore drawing errors in compatibility wrapper
            return

    def circle(
        self,
        x: float,
        y: float,
        d_or_w: float,
        h: float | None = None,
        fill: Optional[tuple[int, ...]] = None,
        stroke: Optional[tuple[int, ...]] = None,
        stroke_weight: Optional[int] = None,
        stroke_width: Optional[int] = None,
    ) -> None:
        """Draw a circle. Call as `circle(x,y,d)` or `circle(x,y,w,h)`.

        If `h` is None the third parameter is treated as a diameter (used for both
        width and height). Per-call style overrides are supported like `ellipse()`.
        """
        if self.surface is None:
            return
        if h is None:
            w = float(d_or_w)
            hh = float(d_or_w)
        else:
            w = float(d_or_w)
            hh = float(h)

        # forward to Surface.circle if available; otherwise fall back to ellipse
        try:
            if hasattr(self.surface, "circle"):
                self.surface.circle(x, y, w, fill=fill, stroke=stroke, stroke_weight=stroke_weight, stroke_width=stroke_width)
                return
        except Exception:
            pass

        # fallback to ellipse API: use w and hh
        try:
            self.surface.ellipse(x, y, w, hh, fill=fill, stroke=stroke, stroke_weight=stroke_weight)
        except Exception:
            return

    # --- Run loop ---
    def initialize(self, debug: bool = False) -> None:
        """Prepare the sketch for running without entering the main loop.

        This runs the user's `setup()`, creates the display surface, applies
        any pending state that was set before the surface existed, marks the
        sketch as ready, and flushes any queued events so user handlers will
        see an initialized sketch. Tests or tooling can call this instead of
        running the full `run()` loop when they only need initialization.
        """
        if debug:
            print("[pycreative.initialize] debug: initializing pygame")
        pygame.init()
        if debug:
            print(f"[pycreative.initialize] debug: sketch_path={self.sketch_path}, width={self.width}, height={self.height}, fullscreen={self.fullscreen}")
        sketch_dir = os.path.dirname(self.sketch_path) if self.sketch_path else os.getcwd()
        try:
            self.assets = Assets(sketch_dir, debug=debug)
        except Exception:
            self.assets = None

        try:
            # Mark not-ready while we run setup/display creation so any
            # incoming events during this window are buffered and flushed
            # once initialization completes.
            try:
                self._setup_complete = False
            except Exception:
                pass
            self.setup()
        except Exception:
            raise

        flags = 0
        if self.fullscreen:
            flags = pygame.FULLSCREEN
        if getattr(self, "_double_buffer", False):
            try:
                flags |= pygame.DOUBLEBUF
            except Exception:
                pass

        try:
            if debug:
                print(f"[pycreative.initialize] debug: creating display mode w={self.width} h={self.height} flags={flags} vsync={getattr(self,'_vsync',0)}")
            self._surface = pygame.display.set_mode((self.width, self.height), flags, vsync=getattr(self, "_vsync", 0))
        except TypeError:
            if debug:
                print("[pycreative.initialize] debug: set_mode with vsync kwarg failed, falling back to positional call")
            self._surface = pygame.display.set_mode((self.width, self.height), flags)
        # record that initialize created the display so run() won't recreate it
        try:
            self._display_created_by_initialize = True
        except Exception:
            pass

        pygame.display.set_caption(self._title)
        # `self._surface` is typed as Optional[pygame.Surface]; cast here to
        # satisfy type checkers that expect a concrete pygame.Surface at this
        # callsite. We guard for None above, so this cast is safe at runtime.
        self.surface = GraphicsSurface(cast(pygame.Surface, self._surface))
        # Apply pending state (color mode, fill, stroke, background, modes)
        try:
            if debug:
                print("[pycreative.initialize] debug: applying pending state to Surface")
            # apply pending color mode first so pending fill/stroke are interpreted correctly
            if getattr(self, "_pending_color_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    cm = self._pending_color_mode
                    if isinstance(cm, tuple) and len(cm) >= 4:
                        if len(cm) >= 5:
                            self.surface.color_mode(cm[0], cm[1], cm[2], cm[3], cm[4])
                        else:
                            self.surface.color_mode(cm[0], cm[1], cm[2], cm[3])
                except Exception:
                    pass

            if self._pending_fill is not _PENDING_UNSET:
                # Safely coerce pending color-like values to concrete tuples.
                def _to_color_tuple(v: object) -> ColorTupleOrNone:
                    if v is None:
                        return None
                    try:
                        # Only call tuple() on iterables
                        if isinstance(v, Iterable) and not isinstance(v, (str, bytes, bytearray)):
                            return tuple(v)
                    except Exception:
                        pass
                    return None

                val = _to_color_tuple(self._pending_fill)
                if debug:
                    print(f"[pycreative.initialize] debug: applying pending fill={val}")
                self.surface.fill(val)
            if self._pending_stroke is not _PENDING_UNSET:
                def _to_color_tuple(v: object) -> ColorTupleOrNone:
                    if v is None:
                        return None
                    try:
                        if isinstance(v, Iterable) and not isinstance(v, (str, bytes, bytearray)):
                            return tuple(v)
                    except Exception:
                        pass
                    return None

                col = _to_color_tuple(self._pending_stroke)
                if debug:
                    print(f"[pycreative.initialize] debug: applying pending stroke={col}")
                self.surface.stroke(col)
            if self._pending_stroke_weight is not _PENDING_UNSET:
                if isinstance(self._pending_stroke_weight, int):
                    self.surface.stroke_weight(self._pending_stroke_weight)

            if getattr(self, "_pending_line_cap", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    v = self._pending_line_cap
                    if v is None:
                        self.surface.set_line_cap("butt")
                    else:
                        self.surface.set_line_cap(v)
                except Exception:
                    pass
            if getattr(self, "_pending_line_join", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    v = self._pending_line_join
                    if v is None:
                        self.surface.set_line_join("miter")
                    else:
                        self.surface.set_line_join(v)
                except Exception:
                    pass
            if getattr(self, "_pending_background", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    bg = self._pending_background
                    if bg is not _PENDING_UNSET:
                        # Try a safe coercion path: prefer concrete tuple forms,
                        # then fall back to Color instances. Avoid passing raw
                        # unknown types to Surface.clear to satisfy static checkers.
                        def _to_color_tuple_local(v: object) -> ColorTupleOrNone:
                            if v is None:
                                return None
                            try:
                                if isinstance(v, Iterable) and not isinstance(v, (str, bytes, bytearray)):
                                    return tuple(v)
                            except Exception:
                                pass
                            return None

                        coerced_bg = _to_color_tuple_local(bg)
                        if coerced_bg is not None:
                            try:
                                # coerced_bg is a concrete tuple of ints (3 or 4-length)
                                self.surface.clear(coerced_bg)
                            except Exception:
                                pass
                        else:
                            # Accept explicit Color instances or numeric grayscale.
                            try:
                                from .color import Color as _Color

                                if isinstance(bg, _Color):
                                    try:
                                        self.surface.clear(bg)
                                    except Exception:
                                        pass
                                elif isinstance(bg, (int, float)):
                                    try:
                                        self.surface.clear(int(bg) & 255)
                                    except Exception:
                                        pass
                                elif isinstance(bg, tuple):
                                    # Ensure tuple is 3- or 4-length of ints before passing
                                    try:
                                        if len(bg) in (3, 4):
                                            t3 = tuple(int(x) for x in bg)
                                            # mypy wants concrete fixed-size tuple types; cast to ColorInput
                                            self.surface.clear(cast(ColorInput, t3))
                                    except Exception:
                                        pass
                            except Exception:
                                # If Color import failed, fall back to guarded tuple/numeric handling
                                if isinstance(bg, (int, float)):
                                    try:
                                        self.surface.clear(int(bg) & 255)
                                    except Exception:
                                        pass
                                elif isinstance(bg, tuple):
                                    try:
                                        if len(bg) in (3, 4):
                                            t3 = tuple(int(x) for x in bg)
                                            self.surface.clear(cast(ColorInput, t3))
                                    except Exception:
                                        pass
                        self._pending_background = _PENDING_UNSET
                except Exception:
                    pass
            if getattr(self, "_pending_rect_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    rm = self._pending_rect_mode
                    if isinstance(rm, str) or rm is None:
                        self.surface.rect_mode(rm)
                except Exception:
                    pass
            if getattr(self, "_pending_ellipse_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    em = self._pending_ellipse_mode
                    if isinstance(em, str) or em is None:
                        self.surface.ellipse_mode(em)
                except Exception:
                    pass
            if getattr(self, "_pending_image_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    im = self._pending_image_mode
                    if isinstance(im, str) or im is None:
                        self.surface.image_mode(im)
                except Exception:
                    pass
            if getattr(self, "_pending_tint", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    t = self._pending_tint
                    if t is None:
                        self.surface.tint(None)
                    else:
                        # t may be raw args tuple recorded by Sketch.tint
                        if isinstance(t, tuple):
                            self.surface.tint(*t)
                        else:
                            self.surface.tint(t)
                except Exception:
                    pass
            if getattr(self, "_pending_blend", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    b = self._pending_blend
                    if b is None:
                        self.surface.blend_mode(None)
                    else:
                        self.surface.blend_mode(b)
                except Exception:
                    pass
        except Exception:
            pass
        # Mark ready and flush any buffered events
        try:
            self._setup_complete = True
        except Exception:
            pass
        try:
            q = getattr(self, "_pending_event_queue", None)
            if q:
                try:
                    from . import input as input_mod_inner
                    while q:
                        ev = q.pop(0)
                        try:
                            input_mod_inner.dispatch_event_now(self, ev)
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

    def run(self, max_frames: Optional[int] = None, debug: bool = False) -> None:
        # Initialize runtime (setup(), display/pending state, queued-event flush)
        self.initialize(debug=debug)
        if debug:
            print("[pycreative.run] debug: entering main loop")

        flags = 0
        if self.fullscreen:
            flags = pygame.FULLSCREEN
        # prefer double buffering when requested
        if getattr(self, "_double_buffer", False):
            try:
                flags |= pygame.DOUBLEBUF
            except Exception:
                # older pygame variants may not expose DOUBLEBUF; ignore
                pass

        # Attempt to pass vsync where supported (pygame 2.0+ may accept a vsync kwarg)
        # If initialize() already created the display surface, reuse it rather
        # than re-creating a new display surface which would clobber any
        # previously-applied pending background/state.
        if getattr(self, "_display_created_by_initialize", False):
            if debug:
                print("[pycreative.run] debug: initialize() created display; reusing existing surface")
            self._surface = pygame.display.get_surface()
        else:
            try:
                # some pygame builds accept vsync as keyword argument
                if debug:
                    print(f"[pycreative.run] debug: creating display mode w={self.width} h={self.height} flags={flags} vsync={self._vsync}")
                self._surface = pygame.display.set_mode((self.width, self.height), flags, vsync=self._vsync)
            except TypeError:
                # fallback to positional set_mode without vsync
                if debug:
                    print("[pycreative.run] debug: set_mode with vsync kwarg failed, falling back to positional call")
                self._surface = pygame.display.set_mode((self.width, self.height), flags)
        if debug:
            try:
                ds = pygame.display.get_surface()
                print(f"[pycreative.run] debug: pygame.display.get_surface() -> {None if ds is None else 'surface'}")
            except Exception as _:
                print("[pycreative.run] debug: pygame.display.get_surface() raised an exception")
            try:
                if self._surface is None:
                    print("[pycreative.run] debug: set_mode returned None (no surface)")
                else:

                    # Prepare a typed `sz` variable once to satisfy static checkers.
                    sz: tuple[Optional[int], Optional[int]] = (None, None)
                    try:
                        maybe_size = self._surface.get_size()
                        # `get_size()` should return (int, int) but guard in case of error
                        sz = (maybe_size[0], maybe_size[1])
                    except Exception:
                        # keep the default (None, None)
                        pass
                    try:
                        flags_now = self._surface.get_flags()
                    except Exception:
                        flags_now = None
                    print(f"[pycreative.run] debug: created surface size={sz} flags={flags_now}")
            except Exception:
                pass
        pygame.display.set_caption(self._title)
        # Same cast as earlier: ensure the typechecker knows this is a pygame.Surface.
        self.surface = GraphicsSurface(cast(pygame.Surface, self._surface))
        # Apply any drawing state set earlier in setup() before the Surface existed
        try:
            if debug:
                print("[pycreative.run] debug: applying pending state to Surface")
            # apply pending color mode first so pending fill/stroke are interpreted correctly
            if getattr(self, "_pending_color_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    cm = self._pending_color_mode
                    # cm may be (mode, max1, max2, max3) or include a 5th alpha max
                    if isinstance(cm, tuple) and len(cm) >= 4:
                        if len(cm) >= 5:
                            self.surface.color_mode(cm[0], cm[1], cm[2], cm[3], cm[4])
                        else:
                            self.surface.color_mode(cm[0], cm[1], cm[2], cm[3])
                except Exception:
                    pass

            if self._pending_fill is not _PENDING_UNSET:
                # explicit None means disable fill; narrow type for static checkers
                def _to_color_tuple(v: object) -> ColorTupleOrNone:
                    if v is None:
                        return None
                    try:
                        if isinstance(v, Iterable) and not isinstance(v, (str, bytes, bytearray)):
                            return tuple(v)
                    except Exception:
                        pass
                    return None

                val = _to_color_tuple(self._pending_fill)
                if debug:
                    print(f"[pycreative.run] debug: applying pending fill={val}")
                self.surface.fill(val)
            if self._pending_stroke is not _PENDING_UNSET:
                def _to_color_tuple(v: object) -> ColorTupleOrNone:
                    if v is None:
                        return None
                    try:
                        if isinstance(v, Iterable) and not isinstance(v, (str, bytes, bytearray)):
                            return tuple(v)
                    except Exception:
                        pass
                    return None

                col = _to_color_tuple(self._pending_stroke)
                if debug:
                    print(f"[pycreative.run] debug: applying pending stroke={col}")
                self.surface.stroke(col)
            if self._pending_stroke_weight is not _PENDING_UNSET:
                if isinstance(self._pending_stroke_weight, int):
                    self.surface.stroke_weight(self._pending_stroke_weight)
            # apply pending line cap/join if present
            if getattr(self, "_pending_line_cap", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    v = self._pending_line_cap
                    if v is None:
                        self.surface.set_line_cap("butt")
                    else:
                        self.surface.set_line_cap(v)
                except Exception:
                    pass
            if getattr(self, "_pending_line_join", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    v = self._pending_line_join
                    if v is None:
                        self.surface.set_line_join("miter")
                    else:
                        self.surface.set_line_join(v)
                except Exception:
                    pass
            # apply pending background if present
            if getattr(self, "_pending_background", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    bg = self._pending_background
                    if bg is not _PENDING_UNSET:
                        # Reuse safe coercion path to avoid unsafe casts here
                        def _to_color_tuple_local(v: object) -> ColorTupleOrNone:
                            if v is None:
                                return None
                            try:
                                from collections.abc import Sequence as _Seq

                                if isinstance(v, _Seq) and not isinstance(v, (str, bytes, bytearray)):
                                    return tuple(v)
                            except Exception:
                                pass
                            return None

                        coerced_bg = _to_color_tuple_local(bg)
                        if coerced_bg is not None:
                            try:
                                self.surface.clear(coerced_bg)
                            except Exception:
                                pass
                        else:
                            try:
                                from .color import Color as _Color

                                if isinstance(bg, _Color):
                                    try:
                                        self.surface.clear(bg)
                                    except Exception:
                                        pass
                                elif isinstance(bg, (int, float)):
                                    try:
                                        self.surface.clear(int(bg) & 255)
                                    except Exception:
                                        pass
                                elif isinstance(bg, tuple):
                                    try:
                                        if len(bg) in (3, 4):
                                            t3 = tuple(int(x) for x in bg)
                                            self.surface.clear(cast(ColorInput, t3))
                                    except Exception:
                                        pass
                            except Exception:
                                # Last-resort guarded handling without importing Color
                                if isinstance(bg, (int, float)):
                                    try:
                                        self.surface.clear(int(bg) & 255)
                                    except Exception:
                                        pass
                                elif isinstance(bg, tuple):
                                    try:
                                        if len(bg) in (3, 4):
                                            t3 = tuple(int(x) for x in bg)
                                            self.surface.clear(cast(ColorInput, t3))
                                    except Exception:
                                        pass
                        self._pending_background = _PENDING_UNSET
                except Exception:
                    pass
            # apply pending rect/ellipse modes if set in setup()
            if getattr(self, "_pending_rect_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    rm = self._pending_rect_mode
                    if isinstance(rm, str) or rm is None:
                        self.surface.rect_mode(rm)
                except Exception:
                    pass
            if getattr(self, "_pending_ellipse_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    em = self._pending_ellipse_mode
                    if isinstance(em, str) or em is None:
                        self.surface.ellipse_mode(em)
                except Exception:
                    pass
        except Exception:
            # best-effort; don't fail startup for state application
            pass
        # Mark setup as complete and flush any buffered events that arrived
        # during early initialization. This ensures user handlers see a
        # fully-initialized sketch (attributes created in setup()) and avoids
        # surprising AttributeError when tests/imports call handlers early.
        try:
            # mark ready so dispatch_event will not queue further events
            self._setup_complete = True
        except Exception:
            pass
        try:
            # Flush any queued raw pygame.Event objects by dispatching them
            # immediately using the internal dispatch helper.
            q = getattr(self, "_pending_event_queue", None)
            if q:
                # import here to avoid circular import at module load
                try:
                    from . import input as input_mod_inner

                    # drain queue in FIFO order
                    while q:
                        ev = q.pop(0)
                        try:
                            input_mod_inner.dispatch_event_now(self, ev)
                        except Exception:
                            # swallow errors to avoid failing startup
                            pass
                except Exception:
                    # if flushing fails, drop events
                    pass
        except Exception:
            pass
        if debug:
            print("[pycreative.run] debug: entering main loop")
        if debug:
            try:
                print(f"[pycreative.run] debug: SDL_VIDEODRIVER={os.environ.get('SDL_VIDEODRIVER')}")
                print(f"[pycreative.run] debug: pygame.display.get_driver()={pygame.display.get_driver()}")
                try:
                    info = pygame.display.Info()
                    print(f"[pycreative.run] debug: display.Info() current_w={info.current_w} current_h={info.current_h} bitsize={info.bitsize}")
                except Exception:
                    print("[pycreative.run] debug: pygame.display.Info() not available")
            except Exception:
                pass
        # Start the main loop: initialize clock and enter run loop
        self._clock = pygame.time.Clock()
        self._running = True

        last_time = time.perf_counter()
        while self._running:
            now = time.perf_counter()
            dt = now - last_time
            last_time = now

            if debug:
                print(f"[pycreative.run] debug: frame loop start frame={self.frame_count} dt={dt:.6f}")

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._running = False
                else:
                    input_mod.dispatch_event(self, ev)

            # Reset transform state at the start of each frame so calls like
            # `self.translate(...)` in `draw()` behave like Processing (not
            # cumulative across frames). Users who need persistent transforms
            # can manage the matrix manually.
            try:
                if self.surface is not None:
                    self.surface.reset_matrix()
            except Exception:
                pass

            if debug:
                print("[pycreative.run] debug: events processed, now calling update/draw")

            try:
                if debug:
                    print("[pycreative.run] debug: calling update()")
                self.update(dt)
                # Respect runtime no-loop mode: if enabled, call draw() only once
                if getattr(self, "_no_loop_mode", False):
                    if not getattr(self, "_has_drawn_once", False):
                        if debug:
                            print("[pycreative.run] debug: calling draw() once due to no_loop")
                        # mark that we're entering draw so no_loop() can detect it
                        self._in_draw = True
                        try:
                            self.draw()
                        finally:
                            self._in_draw = False
                        self._has_drawn_once = True
                else:
                    if debug:
                        print("[pycreative.run] debug: calling draw()")
                    # mark draw in-flight so runtime calls to no_loop() know context
                    self._in_draw = True
                    try:
                        self.draw()
                    finally:
                        self._in_draw = False
            except Exception:
                # On error, attempt teardown and stop
                try:
                    self.teardown()
                finally:
                    self._running = False
                    raise

            if debug:
                print(f"[pycreative.run] debug: calling pygame.display.flip() for frame={self.frame_count}")
            pygame.display.flip()
            if debug:
                try:
                    surf = pygame.display.get_surface()
                    print(f"[pycreative.run] debug: pygame.display.get_surface() exists={surf is not None}")
                except Exception:
                    pass
            self.frame_count += 1
            # If max_frames is provided, stop after reaching it
            if max_frames is not None and self.frame_count >= int(max_frames):
                self._running = False
            # enforce framerate
            if self._clock is not None:
                self._clock.tick(self._frame_rate)

        # Clean up
        try:
            self.teardown()
        finally:
            if debug:
                print("[pycreative.run] debug: quitting pygame and exiting run loop")
            pygame.quit()

    def map(self, value: float, start1: float, stop1: float, start2: float, stop2: float) -> float:
        """Re-map a number from one range to another (Processing.map equivalent).

        Formula: start2 + (value - start1) * (stop2 - start2) / (stop1 - start1)
        Does not clamp the output.
        """
        try:
            v = float(value)
            s1 = float(start1)
            e1 = float(stop1)
            s2 = float(start2)
            e2 = float(stop2)
            if e1 == s1:
                # avoid division by zero: return start2 as best-effort
                return float(s2)
            return s2 + (v - s1) * (e2 - s2) / (e1 - s1)
        except Exception:
            return 0.0

    def noise(self, x: float, y: float | None = None) -> float:
        """Return 1D or 2D Perlin noise in range [0,1].

        Usage:
          self.noise(x)
          self.noise(x, y)
        """
        try:
            from .noise import noise as _noise

            if y is None:
                return float(_noise(float(x)))
            return float(_noise(float(x), float(y)))
        except Exception:
            return 0.0

    def noise_seed(self, seed: int | None) -> None:
        """Reseed the perlin noise generator used by `noise()`.

        Pass `None` to create a random seed.
        """
        try:
            from .noise import seed as _seed

            _seed(seed)
        except Exception:
            pass

    # --- Small math convenience wrappers (Processing-style helpers) ---
    def cos(self, x: float) -> float:
        return self.math.cos(x)

    def sin(self, x: float) -> float:
        return self.math.sin(x)

    def tan(self, x: float) -> float:
        return self.math.tan(x)

    def atan2(self, y: float, x: float) -> float:
        return self.math.atan2(y, x)

    def sqrt(self, x: float) -> float:
        return self.math.sqrt(x)

    def pow(self, x: float, y: float) -> float:
        return self.math.pow(x, y)

    def floor(self, x: float) -> int:
        return self.math.floor(x)

    def ceil(self, x: float) -> int:
        return self.math.ceil(x)

    def radians(self, x: float) -> float:
        return self.math.radians(x)

    def degrees(self, x: float) -> float:
        return self.math.degrees(x)

    # pvector is provided as an instance attribute (factory) in __init__.
    # The older method-style implementation was removed to avoid shadowing
    # and static-analysis confusion. The instance-assigned factory supports
    # both callable creation and class-style helpers (add/sub/etc.).


    def create_graphics(self, w: int, h: int, inherit_state: bool = False, inherit_transform: bool = False) -> OffscreenSurface:
        """Create an offscreen drawing surface matching the public Surface API.

        Returns an `OffscreenSurface` which supports the same primitives as
        the main surface and can be blitted via `blit_image` or `blit`.
        """
        surf = pygame.Surface((int(w), int(h)), flags=pygame.SRCALPHA)
        off = OffscreenSurface(surf)
        if inherit_state:
            if self.surface is not None:
                # copy drawing state from main surface to the offscreen surface
                try:
                    off._fill = getattr(self.surface, "_fill", off._fill)
                    off._stroke = getattr(self.surface, "_stroke", off._stroke)
                    off._stroke_weight = getattr(self.surface, "_stroke_weight", off._stroke_weight)
                    off._rect_mode = getattr(self.surface, "_rect_mode", off._rect_mode)
                    off._ellipse_mode = getattr(self.surface, "_ellipse_mode", off._ellipse_mode)
                    # line styling
                    off._line_cap = getattr(self.surface, "_line_cap", off._line_cap)
                    off._line_join = getattr(self.surface, "_line_join", off._line_join)
                except Exception:
                    # best-effort; don't fail create_graphics if copying fails
                    pass
            else:
                # No live surface to copy from; copy any pending Sketch state
                try:
                    if getattr(self, "_pending_color_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                        off._color_mode = tuple(self._pending_color_mode)
                    if getattr(self, "_pending_fill", _PENDING_UNSET) is not _PENDING_UNSET:
                        # attempt to coerce pending fill using off surface
                        try:
                            coerced = off._coerce_input_color(self._pending_fill)
                            off._fill = cast(ColorTupleOrNone, tuple(coerced)) if coerced is not None else None
                        except Exception:
                            off._fill = getattr(self, "_pending_fill", off._fill)
                    if getattr(self, "_pending_stroke", _PENDING_UNSET) is not _PENDING_UNSET:
                        try:
                            coerced_s = off._coerce_input_color(self._pending_stroke)
                            off._stroke = cast(ColorTupleOrNone, tuple(coerced_s)) if coerced_s is not None else None
                        except Exception:
                            off._stroke = getattr(self, "_pending_stroke", off._stroke)
                    if getattr(self, "_pending_stroke_weight", _PENDING_UNSET) is not _PENDING_UNSET:
                        off._stroke_weight = int(self._pending_stroke_weight)
                    if getattr(self, "_pending_rect_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                        if isinstance(self._pending_rect_mode, str):
                            off._rect_mode = self._pending_rect_mode
                    if getattr(self, "_pending_ellipse_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                        if isinstance(self._pending_ellipse_mode, str):
                            off._ellipse_mode = self._pending_ellipse_mode
                    # copy pending cap/join into offscreen when present
                    if getattr(self, "_pending_line_cap", _PENDING_UNSET) is not _PENDING_UNSET:
                        try:
                            if self._pending_line_cap is None:
                                off.set_line_cap("butt")
                            else:
                                off.set_line_cap(self._pending_line_cap)
                        except Exception:
                            pass
                    if getattr(self, "_pending_line_join", _PENDING_UNSET) is not _PENDING_UNSET:
                        try:
                            if self._pending_line_join is None:
                                off.set_line_join("miter")
                            else:
                                off.set_line_join(self._pending_line_join)
                        except Exception:
                            pass
                except Exception:
                    pass
        # Optionally inherit transform matrix from the active surface
        if inherit_transform and self.surface is not None:
            try:
                off.set_matrix(self.surface.get_matrix())
            except Exception:
                pass
        return off

    # --- Caching helpers ---
    def cache_once(self, key: str, factory: Callable[[], Any]) -> Any:
        """Run a factory once and cache its result by key.

        Typical usage: cache expensive offscreen renders so they only run once.
        """
        if key not in self._cache_store:
            try:
                self._cache_store[key] = factory()
            except Exception:
                # don't crash the sketch if cache creation fails
                self._cache_store[key] = None
        return self._cache_store[key]

    def clear_cache(self, key: Optional[str] = None) -> None:
        """Clear a specific cache entry or the entire cache if key is None."""
        if key is None:
            self._cache_store.clear()
        else:
            self._cache_store.pop(key, None)

    def cached_graphics(self, key: str, w: int, h: int, render_fn: Callable[[OffscreenSurface], None]) -> OffscreenSurface:
        """Create or return a cached OffscreenSurface produced by `render_fn`.

        `render_fn` is called once with an `OffscreenSurface` argument and should
        draw into it. The resulting OffscreenSurface is cached under `key`.
        """
        def factory() -> OffscreenSurface:
            off = self.create_graphics(w, h)
            try:
                with off:
                    render_fn(off)
            except Exception:
                # swallow render errors during cache generation
                pass
            return off

        return self.cache_once(key, factory)

    # --- Convenience helpers: cached graphics and runtime no-loop control ---
    def no_loop(self, *args, **kwargs):
        """Dual-purpose helper:

        - no_loop(key, w, h, render_fn) -> OffscreenSurface
          Backwards-compatible alias for `cached_graphics` (existing behavior).

        - no_loop() -> None
          When called with no arguments, toggles runtime "no-loop" mode: the
          `draw()` method will be called once and then suppressed until `loop()`
          is called to resume continuous rendering.
        """
        # runtime no-loop: called without args
        if len(args) == 0 and len(kwargs) == 0:
            self._no_loop_mode = True
            # If called from inside draw(), consider the current draw as the
            # single draw and mark it done to avoid a second draw in the same
            # frame. Otherwise reset _has_drawn_once so the next loop will
            # perform one draw when the mode is active.
            if getattr(self, "_in_draw", False):
                self._has_drawn_once = True
            else:
                self._has_drawn_once = False
            return None

        # otherwise, forward to cached_graphics for backward compatibility
        return self.cached_graphics(*args, **kwargs)

    def loop(self) -> None:
        """Resume continuous drawing after a prior `no_loop()` call."""
        self._no_loop_mode = False
        self._has_drawn_once = False

    def no_loop_graphics(self, *args, **kwargs) -> OffscreenSurface | None:
        """Backward-compatible alias name for cached_graphics/no_loop.

        May return an OffscreenSurface when used as a cached-graphics helper,
        or None when called as the runtime no_loop() toggle.
        """
        return self.no_loop(*args, **kwargs)
