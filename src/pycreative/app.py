from __future__ import annotations

from typing import Optional, Tuple, Callable, Any, cast

import time
import os
import pygame

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

    def __init__(self, sketch_path: Optional[str] = None) -> None:
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
        self._cache_store = {}
        # Pending drawing state if user sets it before the Surface is created.
        # Use a sentinel to distinguish "no pending change" from an explicit
        # `None` (which means disable fill/stroke).
        self._pending_fill = _PENDING_UNSET
        self._pending_stroke = _PENDING_UNSET
        self._pending_stroke_weight = _PENDING_UNSET
        # Pending cursor visibility state: use sentinel to distinguish
        # "no pending change" from an explicit show/hide request.
        self._pending_cursor = _PENDING_UNSET
        # By default, pressing Escape closes the sketch; this can be disabled
        # by calling `self.set_escape_closes(False)` in the sketch.
        self._escape_closes = True
        # Pending shape mode state for rect/ellipse - allow setting in setup()
        self._pending_rect_mode = _PENDING_UNSET
        self._pending_ellipse_mode = _PENDING_UNSET
        # Pending color mode (e.g., set in setup before surface exists)
        self._pending_color_mode = _PENDING_UNSET

        # Runtime no-loop control (if True, draw() runs once then is suppressed)
        self._no_loop_mode = False
        self._has_drawn_once = False

        # Optional per-sketch snapshots folder (preferred over env var)
        # Can be set by assignment: `self.save_folder = 'snapshots'` or via
        # the helper `self.set_save_folder('snapshots')`.
        # Use a plain assignment (no forward annotation) to avoid static
        # analysis issues in older type-checkers.
        self._save_folder = None
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
                # pull the function object from the base Sketch and set it on the subclass
                func = getattr(Sketch, name, None)
                if func is not None:
                    setattr(cls, name, func)

    # --- Lifecycle hooks (override in subclasses) ---
    def setup(self) -> None:
        return None

    def update(self, dt: float) -> None:
        return None

    def draw(self) -> None:
        return None

    def on_event(self, event: input_mod.Event) -> None:
        return None

    def teardown(self) -> None:
        return None

    # --- Helpers ---
    def size(self, w: int, h: int, fullscreen: bool = False) -> None:
        self.width = int(w)
        self.height = int(h)
        self.fullscreen = bool(fullscreen)

    def set_save_folder(self, folder: Optional[str]) -> None:
        """Set a per-sketch snapshots folder.

        Example:
            self.set_save_folder('snapshots')

        This preferred per-sketch value will be used by `save_snapshot()` when
        resolving relative paths. Use `None` to clear and fall back to the
        environment variable (if present) or the sketch directory.
        """
        self._save_folder = None if folder is None else str(folder)

    @property
    def save_folder(self) -> Optional[str]:
        """Property alias for the per-sketch snapshots folder.

        You can set this directly in a sketch: `self.save_folder = 'shots'`.
        """
        return self._save_folder

    @save_folder.setter
    def save_folder(self, folder: Optional[str]) -> None:
        self.set_save_folder(folder)

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
    def fill(self, color: Optional[Tuple[int, int, int]]):
        if self.surface is not None:
            self.surface.fill(color)
        else:
            self._pending_fill = color

    def no_fill(self) -> None:
        if self.surface is not None:
            self.surface.no_fill()
        else:
            self._pending_fill = None

    def stroke(self, color: Optional[Tuple[int, int, int]]):
        if self.surface is not None:
            self.surface.stroke(color)
        else:
            self._pending_stroke = color

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
        if mode in (GraphicsSurface.MODE_CORNER, GraphicsSurface.MODE_CENTER):
            self._pending_rect_mode = mode
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
        if mode in (GraphicsSurface.MODE_CORNER, GraphicsSurface.MODE_CENTER):
            self._pending_ellipse_mode = mode
        return None

    def color_mode(self, mode: Optional[str] = None, max1: int = 255, max2: int = 255, max3: int = 255):
        """Get or set color mode. When called before a Surface exists this
        records a pending color_mode tuple which will be applied in run().
        """
        if self.surface is not None:
            return self.surface.color_mode(mode, max1, max2, max3)
        if mode is None:
            v = self._pending_color_mode
            if v is _PENDING_UNSET:
                return None
            return cast(tuple, v)
        try:
            m = str(mode).upper()
            if m in ("RGB", "HSB"):
                self._pending_color_mode = (m, int(max1), int(max2), int(max3))
        except Exception:
            pass
        return None

    def text(self, txt: str, x: int, y: int, font_name: Optional[str] = None, size: int = 24, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        if self.surface is not None:
            self.surface.text(txt, x, y, font_name=font_name, size=size, color=color)

    def load_image(self, path: str) -> object:
        """Load an image using the Assets manager if available.

        The Assets manager searches sketch/data and the sketch directory and caches images.
        """
        # prefer assets manager which handles resolution and caching
        try:
            if hasattr(self, "assets") and self.assets:
                img = self.assets.load_image(path)
                if img is not None:
                    return OffscreenSurface(getattr(img, "raw", img))
        except Exception as e:
            print(f"Sketch: Assets.load_image failed for '{path}': {e}")

        # fallback to surface loader if available
        try:
            if self.surface is not None:
                img = self.surface.load_image(path)
                # surface.load_image returns a pygame.Surface; wrap in OffscreenSurface
                if img is not None:
                    return OffscreenSurface(getattr(img, "raw", img))
        except Exception:
            pass

        # final fallback to pygame
        try:
            img = pygame.image.load(path)
            return OffscreenSurface(img)
        except Exception:
            print(f"Failed to load image: {path}")
            return None

    def blit_image(self, img: object, x: int = 0, y: int = 0) -> None:
        if self.surface is not None and img is not None:
            self.surface.blit_image(img, x=x, y=y)

    # --- Backwards-compatible primitive wrappers (old example APIs) ---
    def line(self, x1, y1, x2, y2, stroke: Optional[Tuple[int, int, int]] = None, stroke_width: Optional[int] = None, cap: Optional[str] = None, join: Optional[str] = None):
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

    def triangle(self, x1, y1, x2, y2, x3, y3, fill: Optional[Tuple[int, int, int]] = None, stroke: Optional[Tuple[int, int, int]] = None, stroke_width: Optional[int] = None):
        if self.surface is None:
            return
        pts = [(x1, y1), (x2, y2), (x3, y3)]
        # forward per-call styles to Surface.polygon_with_style
        self.surface.polygon_with_style(pts, fill=fill, stroke=stroke, stroke_weight=stroke_width)

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4, fill: Optional[Tuple[int, int, int]] = None, stroke: Optional[Tuple[int, int, int]] = None, stroke_width: Optional[int] = None):
        if self.surface is None:
            return
        pts = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        # forward per-call styles to Surface.polygon_with_style for parity
        # with other shape helpers.
        self.surface.polygon_with_style(pts, fill=fill, stroke=stroke, stroke_weight=stroke_width)

    def polyline(self, points: list[tuple[float, float]], stroke: Optional[Tuple[int, int, int]] = None, stroke_width: Optional[int] = None):
        """Draw an open polyline. Accepts list of (x,y) points and optional stroke/stroke_width.

        This temporarily applies stroke settings like other compatibility shims.
        """
        if self.surface is None:
            return
        # forward per-call styles to Surface.polyline_with_style
        self.surface.polyline_with_style(points, stroke=stroke, stroke_weight=stroke_width)

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
        prev_fill = self.surface._fill
        prev_stroke = self.surface._stroke
        prev_sw = self.surface._stroke_weight
        try:
            if fill is not None:
                self.surface.fill(fill)
            if stroke is not None:
                self.surface.stroke(stroke)
            if stroke_width is not None:
                self.surface.stroke_weight(stroke_width)
            self.surface.arc(x, y, w, h, start_rad, end_rad, mode=mode)
        finally:
            self.surface._fill = prev_fill
            self.surface._stroke = prev_stroke
            self.surface._stroke_weight = prev_sw

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

    def radians(self, deg: float) -> float:
        import math

        return math.radians(deg)

    def stroke_width(self, w: int) -> None:
        if self.surface is not None:
            self.surface.stroke_weight(w)

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
        p = self.mouse_pos()
        return int(p[0]) if p is not None else None

    @property
    def mouse_y(self) -> Optional[int]:
        """Return the current mouse y position or None if unavailable."""
        p = self.mouse_pos()
        return int(p[1]) if p is not None else None

    # --- Basic drawing primitives ---
    def clear(self, color: Tuple[int, int, int]) -> None:
        if self.surface is not None:
            self.surface.clear(color)

    def ellipse(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
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

        # Save previous state
        prev_fill = self.surface._fill
        prev_stroke = self.surface._stroke
        prev_stroke_weight = self.surface._stroke_weight

        try:
            if fill is not None:
                self.surface.fill(fill)
            if stroke is not None:
                self.surface.stroke(stroke)
            # accept both stroke_weight and stroke_width for compatibility;
            # prefer stroke_width if provided by caller.
            chosen_sw = None
            if stroke_width is not None:
                chosen_sw = int(stroke_width)
            elif stroke_weight is not None:
                chosen_sw = int(stroke_weight)
            if chosen_sw is not None:
                self.surface.stroke_weight(chosen_sw)

            # forward per-call styles to Surface.ellipse
            self.surface.ellipse(x, y, w, h, fill=fill, stroke=stroke, stroke_weight=chosen_sw)
        finally:
            # Restore previous state
            self.surface._fill = prev_fill
            self.surface._stroke = prev_stroke
            self.surface._stroke_weight = prev_stroke_weight

    # --- Run loop ---
    def run(self, max_frames: Optional[int] = None) -> None:
        pygame.init()
        # Initialize assets manager early so setup() can use it
        sketch_dir = os.path.dirname(self.sketch_path) if self.sketch_path else os.getcwd()
        try:
            self.assets = Assets(sketch_dir)
        except Exception:
            self.assets = None

        # Call setup early so user can call self.size() there
        try:
            self.setup()
        except Exception:
            # setup exceptions should not crash import; re-raise
            raise

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
        try:
            # some pygame builds accept vsync as keyword argument
            self._surface = pygame.display.set_mode((self.width, self.height), flags, vsync=self._vsync)
        except TypeError:
            # fallback to positional set_mode without vsync
            self._surface = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption(self._title)
        self.surface = GraphicsSurface(self._surface)
        # Apply any drawing state set earlier in setup() before the Surface existed
        try:
            # apply pending color mode first so pending fill/stroke are interpreted correctly
            if getattr(self, "_pending_color_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    cm = self._pending_color_mode
                    # cm is a tuple (mode, max1, max2, max3)
                    if isinstance(cm, tuple) and len(cm) == 4:
                        self.surface.color_mode(cm[0], cm[1], cm[2], cm[3])
                except Exception:
                    pass

            if self._pending_fill is not _PENDING_UNSET:
                # explicit None means disable fill
                self.surface.fill(self._pending_fill)
            if self._pending_stroke is not _PENDING_UNSET:
                self.surface.stroke(self._pending_stroke)
            if self._pending_stroke_weight is not _PENDING_UNSET:
                self.surface.stroke_weight(self._pending_stroke_weight)
            # apply pending rect/ellipse modes if set in setup()
            if getattr(self, "_pending_rect_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    self.surface.rect_mode(self._pending_rect_mode)
                except Exception:
                    pass
            if getattr(self, "_pending_ellipse_mode", _PENDING_UNSET) is not _PENDING_UNSET:
                try:
                    self.surface.ellipse_mode(self._pending_ellipse_mode)
                except Exception:
                    pass
        except Exception:
            # best-effort; don't fail startup for state application
            pass
        self._clock = pygame.time.Clock()
        self._running = True

        last_time = time.perf_counter()
        while self._running:
            now = time.perf_counter()
            dt = now - last_time
            last_time = now

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._running = False
                else:
                    input_mod.dispatch_event(self, ev)

            try:
                self.update(dt)
                # Respect runtime no-loop mode: if enabled, call draw() only once
                if getattr(self, "_no_loop_mode", False):
                    if not getattr(self, "_has_drawn_once", False):
                        self.draw()
                        self._has_drawn_once = True
                else:
                    self.draw()
            except Exception:
                # On error, attempt teardown and stop
                try:
                    self.teardown()
                finally:
                    self._running = False
                    raise

            pygame.display.flip()
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
            pygame.quit()

    def create_graphics(self, w: int, h: int, inherit_state: bool = False, inherit_transform: bool = False) -> OffscreenSurface:
        """Create an offscreen drawing surface matching the public Surface API.

        Returns an `OffscreenSurface` which supports the same primitives as
        the main surface and can be blitted via `blit_image` or `blit`.
        """
        surf = pygame.Surface((int(w), int(h)), flags=pygame.SRCALPHA)
        off = OffscreenSurface(surf)
        if inherit_state and self.surface is not None:
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
            self._has_drawn_once = False
            return None

        # otherwise, forward to cached_graphics for backward compatibility
        return self.cached_graphics(*args, **kwargs)

    def loop(self) -> None:
        """Resume continuous drawing after a prior `no_loop()` call."""
        self._no_loop_mode = False
        self._has_drawn_once = False

    def no_loop_graphics(self, *args, **kwargs) -> OffscreenSurface:
        """Backward-compatible alias name for cached_graphics/no_loop."""
        return self.no_loop(*args, **kwargs)
