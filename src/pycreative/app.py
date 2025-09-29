from __future__ import annotations

from typing import Optional, Tuple, Callable, Any

import time
import os
import pygame

from . import input as input_mod
from .graphics import Surface as GraphicsSurface
from .graphics import OffscreenSurface
from .assets import Assets


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
        # Pending drawing state if user sets it before the Surface is created
        self._pending_fill: Optional[Tuple[int, int, int]] = None
        self._pending_stroke: Optional[Tuple[int, int, int]] = None
        self._pending_stroke_weight: Optional[int] = None
        # Runtime no-loop control (if True, draw() runs once then is suppressed)
        self._no_loop_mode = False
        self._has_drawn_once = False

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

    def set_title(self, title: str) -> None:
        self._title = str(title)
        if pygame.display.get_init():
            pygame.display.set_caption(self._title)

    def frame_rate(self, fps: int) -> None:
        self._frame_rate = int(fps)

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

    def rect_mode(self, mode: str) -> None:
        if self.surface is not None:
            self.surface.rect_mode(mode)

    def ellipse_mode(self, mode: str) -> None:
        if self.surface is not None:
            self.surface.ellipse_mode(mode)

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
                return self.assets.load_image(path)
        except Exception as e:
            print(f"Sketch: Assets.load_image failed for '{path}': {e}")

        # fallback to surface loader if available
        try:
            if self.surface is not None:
                return self.surface.load_image(path)
        except Exception:
            pass

        # final fallback to pygame
        try:
            return pygame.image.load(path)
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

    def triangle(self, x1, y1, x2, y2, x3, y3):
        if self.surface is None:
            return
        self.surface.polygon([(x1, y1), (x2, y2), (x3, y3)])

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        if self.surface is None:
            return
        self.surface.polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])

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
        if w is None or h is None:
            self.surface.blit_image(img, int(x), int(y))
            return
        # scale image
        scaled = pygame.transform.smoothscale(img, (int(w), int(h)))
        self.surface.blit_image(scaled, int(x), int(y))

    def radians(self, deg: float) -> float:
        import math

        return math.radians(deg)

    def stroke_width(self, w: int) -> None:
        if self.surface is not None:
            self.surface.stroke_weight(w)

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
            if stroke_weight is not None:
                self.surface.stroke_weight(stroke_weight)

            # forward per-call styles to Surface.ellipse
            self.surface.ellipse(x, y, w, h, fill=fill, stroke=stroke, stroke_weight=stroke_weight)
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

        self._surface = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption(self._title)
        self.surface = GraphicsSurface(self._surface)
        # Apply any drawing state set earlier in setup() before the Surface existed
        try:
            if self._pending_fill is not None:
                self.surface.fill(self._pending_fill)
            if self._pending_stroke is not None:
                self.surface.stroke(self._pending_stroke)
            if self._pending_stroke_weight is not None:
                self.surface.stroke_weight(self._pending_stroke_weight)
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

    def create_graphics(self, w: int, h: int, inherit_state: bool = False) -> OffscreenSurface:
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
