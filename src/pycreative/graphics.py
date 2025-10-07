from __future__ import annotations

from typing import Optional, Tuple
from .types import ColorInput, ColorTupleOrNone, ColorTuple

import pygame
from typing import Any
from contextlib import contextmanager
from pycreative.pixels import get_pixels, set_pixels, get_pixel, set_pixel, pixels as pixels_ctx

from .transforms import (
    identity_matrix,
    multiply,
    translate_matrix,
    rotate_matrix,
    scale_matrix,
    transform_point,
    transform_points,
    decompose_scale,
)
from .color import Color
from pycreative.shape_math import flatten_cubic_bezier, bezier_point, bezier_tangent, curve_point, curve_tangent
from pycreative import primitives as _primitives


# NOTE: numpy support removed — pixel helpers use pure-Python nested lists.
_HAS_NUMPY = False
_np = None


# Pixel helpers delegated to `pycreative.pixels` (see pixels.py)


class Surface:
    """Lightweight wrapper around a pygame.Surface exposing primitives and
    simple drawing state (fill, stroke, stroke weight) and modes.

    - ellipse(x, y, w, h): x,y are center by default
    - rect accepts CORNER (x,y top-left) or CENTER modes
    """

    MODE_CORNER = "CORNER"
    MODE_CENTER = "CENTER"
    MODE_CORNERS = "CORNERS"
    # Processing-style blend mode constants
    BLEND = "BLEND"
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    DARKEST = "DARKEST"
    LIGHTEST = "LIGHTEST"
    DIFFERENCE = "DIFFERENCE"
    EXCLUSION = "EXCLUSION"
    MULTIPLY = "MULTIPLY"
    SCREEN = "SCREEN"
    REPLACE = "REPLACE"

    def __init__(self, surf: pygame.Surface) -> None:
        self._surf = surf
        # Drawing state
        # _fill/_stroke accept either 3- or 4-length tuples (RGB or RGBA)
        # Use the concrete ColorTupleOrNone annotation for internal storage
        self._fill: ColorTupleOrNone = (255, 255, 255)
        self._stroke: ColorTupleOrNone = None
        self._stroke_weight: int = 1
        self._rect_mode: str = self.MODE_CORNER
        self._ellipse_mode: str = self.MODE_CENTER
        # Image mode controls how image(x,y,w,h) interprets x/y (corner vs center)
        self._image_mode: str = self.MODE_CORNER
        # Tint color applied to subsequent image draws; None means no tint.
        # Stored as an already-coerced pygame-friendly tuple (3- or 4-tuple)
        self._tint: ColorTupleOrNone = None
        # Blend mode controls how source pixels combine with destination
        # Default is source-over alpha blend (Processing BLEND)
        self._blend_mode: str = self.BLEND
        # Line styling options (cap: 'butt'|'round'|'square', join: 'miter'|'round'|'bevel')
        self._line_cap: str = "butt"
        self._line_join: str = "miter"
        # shape construction buffer for begin/vertex/end
        # Entries are tuples of form ('v', (x,y)) for simple vertices or
        # ('bz', (cx1, cy1, cx2, cy2, x3, y3)) for a bezier vertex segment.
        self._shape_points: list = []
        # Default sampling detail for bezier flattening (used by bezier())
        self._bezier_detail: int = 20
        # Default sampling/detail and tightness for Catmull-Rom style curves
        self._curve_detail: int = 20
        # Curve tightness: 0.0 => standard Catmull-Rom; 1.0 => zero tangents (looser)
        self._curve_tightness: float = 0.0

        # Transformation stack: list of 3x3 matrices; keep identity as base
        self._matrix_stack: list[list[list[float]]] = [identity_matrix()]
        # Color mode: ('RGB'|'HSB', max1, max2, max3, max4)
        # Defaults mirror common 0-255 ranges. When in HSB mode, fill()/stroke()
        # will interpret tuple inputs as (h,s,b,a) in the configured ranges.
        self._color_mode: tuple[str, int, int, int, int] = ("RGB", 255, 255, 255, 255)
        # Cache for temporary SRCALPHA surfaces keyed by (w,h) to avoid
        # allocating many small surfaces each frame. This is a small, short-
        # lived cache and not intended for long-term memory growth.
        self._temp_surface_cache: dict[tuple[int, int], pygame.Surface] = {}

    def _get_temp_surface(self, w: int, h: int) -> pygame.Surface:
        """Return a cached SRCALPHA temporary surface for the given size.

        This avoids repeated allocations when many small primitives are
        rendered with alpha in a single frame.
        """
        key = (int(w), int(h))
        surf = self._temp_surface_cache.get(key)
        if surf is None or surf.get_size() != (key[0], key[1]):
            surf = pygame.Surface((key[0], key[1]), flags=pygame.SRCALPHA)
            self._temp_surface_cache[key] = surf
        # clear previous contents
        surf.fill((0, 0, 0, 0))
        return surf

    # --- transform stack helpers ---
    def _current_matrix(self):
        return self._matrix_stack[-1]

    def push(self) -> None:
        """Push a copy of the current transform onto the stack."""
        top = self._current_matrix()
        self._matrix_stack.append([row[:] for row in top])

    # Processing-style aliases
    def push_matrix(self) -> None:
        """Alias for push() to match Processing-style API."""
        return self.push()

    def pop(self) -> None:
        """Pop the top transform. The base identity matrix cannot be popped."""
        if len(self._matrix_stack) == 1:
            raise IndexError("cannot pop base transform")
        self._matrix_stack.pop()

    # Processing-style aliases
    def pop_matrix(self) -> None:
        """Alias for pop() to match Processing-style API."""
        return self.pop()

    def translate(self, dx: float, dy: float) -> None:
        """Apply a translation to the current transform."""
        self._matrix_stack[-1] = multiply(self._matrix_stack[-1], translate_matrix(dx, dy))

    def rotate(self, theta: float) -> None:
        """Apply a rotation (radians) to the current transform."""
        self._matrix_stack[-1] = multiply(self._matrix_stack[-1], rotate_matrix(theta))

    def scale(self, sx: float, sy: float | None = None) -> None:
        """Apply a scale to the current transform."""
        self._matrix_stack[-1] = multiply(self._matrix_stack[-1], scale_matrix(sx, sy))

    def reset_matrix(self) -> None:
        """Reset the current (top) matrix to identity."""
        self._matrix_stack[-1] = identity_matrix()

    def get_matrix(self) -> list[list[float]]:
        """Return a copy of the current transform matrix."""
        return [row[:] for row in self._current_matrix()]

    def set_matrix(self, M: list[list[float]]) -> None:
        """Overwrite the current top matrix with M (copied)."""
        self._matrix_stack[-1] = [row[:] for row in M]

    @contextmanager
    def transform(self, translate: tuple[float, float] | None = None, rotate: float | None = None, scale: tuple[float, float] | None = None):
        """Context manager that pushes a transform, applies optional ops, and pops on exit.

        Example:
            with surface.transform(translate=(10,20), rotate=0.3):
                surface.rect(...)
        """
        self.push()
        try:
            if translate is not None:
                self.translate(*translate)
            if rotate is not None:
                self.rotate(rotate)
            if scale is not None:
                sx, sy = scale
                self.scale(sx, sy)
            yield self
        finally:
            self.pop()

    def _is_identity_transform(self) -> bool:
        m = self._current_matrix()
        return (
            m[0][0] == 1.0
            and m[0][1] == 0.0
            and m[0][2] == 0.0
            and m[1][0] == 0.0
            and m[1][1] == 1.0
            and m[1][2] == 0.0
        )

    def _coerce_input_color(self, color_val: ColorInput | None) -> ColorTupleOrNone:
        """Coerce various color inputs into a pygame-friendly tuple.

        Accepts a Color instance, an HSB tuple when color mode is HSB, or an
        RGB(A) tuple. Returns a 3- or 4-tuple suitable for pygame drawing or
        None if input is None.
        """
        if color_val is None:
            return None

        # Accept numeric grayscale shorthand like 255
        try:
            if isinstance(color_val, (int, float)):
                v = int(color_val) & 255
                return (v, v, v)
        except Exception:
            pass

        # helper to clamp numeric channel values into 0..255 (don't wrap negatives)
        def _clamp_byte(v):
            try:
                iv = int(v)
            except Exception:
                return 0
            if iv < 0:
                return 0
            if iv > 255:
                return 255
            return iv

        # Accept Color instances directly
        if isinstance(color_val, Color):
            try:
                return color_val.to_rgba_tuple() if color_val.a != 255 else color_val.to_tuple()
            except Exception:
                return color_val.to_tuple()

        # Determine current color mode
        try:
            mode = self._color_mode[0]
            m1 = int(self._color_mode[1])
        except Exception:
            mode = "RGB"
            m1 = 255

        # If HSB mode and iterable input interpret as HSB
        try:
            if mode == "HSB" and hasattr(color_val, "__iter__"):
                vals = list(color_val)
                h, s, v = vals[0], vals[1], vals[2]
                a = vals[3] if len(vals) >= 4 else 255
                # Use configured alpha max when present (fifth entry in _color_mode)
                ma = int(self._color_mode[4]) if len(self._color_mode) >= 5 else m1
                col = Color.from_hsb(float(h), float(s), float(v), a=a, max_h=m1, max_s=self._color_mode[2], max_v=self._color_mode[3], max_a=ma)
                return col.to_rgba_tuple() if col.a != 255 else col.to_tuple()
        except Exception:
            pass

        # Fallback: treat as RGB(A)
        try:
            if hasattr(color_val, "__iter__"):
                vals = list(color_val)
                r = _clamp_byte(vals[0])
                g = _clamp_byte(vals[1])
                b = _clamp_byte(vals[2])
                if len(vals) >= 4:
                    a = _clamp_byte(vals[3])
                    return (r, g, b, a)
                return (r, g, b)
        except Exception:
            return None

        # Explicit fallback for type-checkers: ensure a None return is present
        return None

    def _transform_point(self, x: float, y: float) -> tuple[float, float]:
        return transform_point(self._current_matrix(), x, y)

    def transform_points(self, pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
        """Apply the current transform to a list of (x,y) points and return transformed points.

        This helper mirrors the standalone `transform_points` in `pycreative.transforms`
        and is used by primitives which call `surface.transform_points(...)` when a
        non-identity transform is active.
        """
        try:
            return transform_points(self._current_matrix(), pts)
        except Exception:
            # Fallback: attempt per-point transform using _transform_point
            return [self._transform_point(float(x), float(y)) for (x, y) in pts]


    # --- pixel view helpers ---
    def is_numpy_backed(self) -> bool:
        """Return True if the surface pixel helpers will return a numpy-backed array."""
        return False

    @property
    def raw(self) -> pygame.Surface:
        """Expose the underlying pygame.Surface for use by helpers (e.g., save)."""
        return self._surf

    def get_size(self) -> tuple[int, int]:
        """Return (width, height) of the underlying surface."""
        return self._surf.get_size()

    # Backwards-compatible methods: tests and some examples call `rect_mode()`
    # and `ellipse_mode()` as setter/getter functions. Provide a method that
    # acts as a getter when called with no arguments and a setter when called
    # with a mode argument.
    def rect_mode(self, mode: str | None = None) -> str | None:
        """Get or set rectangle mode. Call with no args to get current mode,
        or pass `Surface.MODE_CORNER` / `Surface.MODE_CENTER` to set it.
        """
        if mode is None:
            return self._rect_mode
        try:
            m = str(mode).upper()
        except Exception:
            return None
        if m in (self.MODE_CORNER, self.MODE_CENTER):
            self._rect_mode = m
        return None

    def ellipse_mode(self, mode: str | None = None) -> str | None:
        """Get or set ellipse mode. Call with no args to get current mode,
        or pass `Surface.MODE_CORNER` / `Surface.MODE_CENTER` to set it.
        """
        if mode is None:
            return self._ellipse_mode
        try:
            m = str(mode).upper()
        except Exception:
            return None
        if m in (self.MODE_CORNER, self.MODE_CENTER):
            self._ellipse_mode = m
        return None

    def image_mode(self, mode: str | None = None) -> str | None:
        """Get or set image mode. Call with no args to get current mode,
        or pass `Surface.MODE_CORNER` / `Surface.MODE_CENTER` / `Surface.MODE_CORNERS` to set it.
        """
        if mode is None:
            return self._image_mode
        try:
            m = str(mode).upper()
        except Exception:
            return None
        if m in (self.MODE_CORNER, self.MODE_CENTER, self.MODE_CORNERS):
            self._image_mode = m
        return None

    def tint(self, *args) -> Optional[tuple[int, ...]]:
        """Get or set the image tint color. When called with no args returns current tint.

        Accepts Processing-style forms:
          tint(gray)
          tint(gray, alpha)
          tint(r, g, b)
          tint(r, g, b, a)
          tint((r,g,b)) or tint((r,g,b,a))
        """
        # getter
        if len(args) == 0:
            return self._tint

        # normalize args into a single color tuple-like
        if len(args) == 1:
            color_in = args[0]
        else:
            color_in = tuple(args)

        # Support Processing-style shorthand: (gray) or (gray, alpha)
        try:
            if isinstance(color_in, (list, tuple)):
                def _clamp_byte_local(x):
                    try:
                        iv = int(x)
                    except Exception:
                        return 0
                    if iv < 0:
                        return 0
                    if iv > 255:
                        return 255
                    return iv

                if len(color_in) == 1:
                    v = _clamp_byte_local(color_in[0])
                    color_in = (v, v, v)
                elif len(color_in) == 2:
                    v = _clamp_byte_local(color_in[0])
                    a = _clamp_byte_local(color_in[1])
                    color_in = (v, v, v, a)
        except Exception:
            pass

        coerced = self._coerce_input_color(color_in)
        self._tint = coerced
        return None

    def blend_mode(self, mode: str | None = None) -> str | None:
        """Get or set the current blend mode.

        When called with no arguments returns the current blend mode string.
        When called with a string sets the blend mode for subsequent draw
        operations. Accepted values are the Surface.* constants (e.g.
        Surface.ADD, Surface.MULTIPLY, Surface.BLEND, etc.).
        """
        if mode is None:
            return self._blend_mode
        try:
            self._blend_mode = str(mode)
        except Exception:
            pass
        return None

    @property
    def size(self) -> tuple[int, int]:
        """Convenience property returning (width, height) of the surface."""
        return self.get_size()

    def text(self, txt: str, x: int, y: int, font_name: Optional[str] = None, size: int = 24, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Render text onto the surface. Provided on Surface for convenience so
        sketches can call `self.surface.text(...)` regardless of whether the
        surface is on- or off-screen.
        """
        try:
            font = pygame.font.SysFont(font_name, int(size))
            surf = font.render(str(txt), True, color)
            self._surf.blit(surf, (int(x), int(y)))
        except Exception:
            # best-effort; don't crash sketches if font rendering isn't available
            return

    # --- basic operations ---
    def clear(self, color: Tuple[int, int, int]) -> None:
        """Fill the entire surface with a color.

        Accepts the same color forms as `fill()`: a `Color` instance, an HSB
        tuple when color mode is HSB, or an RGB tuple of ints.
        """
        # Accept Color instances directly (preserve alpha if present)
        try:
            if isinstance(color, Color):
                try:
                    rgba = color.to_rgba_tuple()
                except Exception:
                    rgba = color.to_tuple()
                self._surf.fill(rgba)
                return
        except Exception:
            pass

        # Accept numeric grayscale shorthand
        try:
            if isinstance(color, (int, float)):
                v = int(color) & 255
                self._surf.fill((v, v, v))
                return
        except Exception:
            pass

        # If HSB color mode is active and a 3-tuple is provided interpret as HSB
        try:
            # support (mode, max1, max2, max3, max4)
            mode, m1, m2, m3, *_rest = self._color_mode
            if mode == "HSB" and hasattr(color, "__iter__"):
                # allow 3- or 4-length tuples: (h,s,v) or (h,s,v,a)
                vals = list(color)
                h, s, v = vals[0], vals[1], vals[2]
                ma = int(self._color_mode[4]) if len(self._color_mode) >= 5 else m1
                col = Color.from_hsb(float(h), float(s), float(v), max_h=m1, max_s=m2, max_v=m3, max_a=ma)
                # if alpha was provided propagate it
                if len(vals) >= 4:
                    a = int(vals[3]) & 255
                    rgba = (col.r, col.g, col.b, a)
                    self._surf.fill(rgba)
                else:
                    self._surf.fill(col.to_tuple())
                return
        except Exception:
            pass

        # fallback: treat as RGB tuple (allow alpha)
        try:
            if hasattr(color, "__iter__"):
                vals = list(color)
                r = int(vals[0]) & 255
                g = int(vals[1]) & 255
                b = int(vals[2]) & 255
                if len(vals) >= 4:
                    a = int(vals[3]) & 255
                    self._surf.fill((r, g, b, a))
                else:
                    self._surf.fill((r, g, b))
                return
        except Exception:
            # best-effort: ignore invalid input
            return

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: Optional[Tuple[int, ...]] = None,
        stroke: Optional[Tuple[int, ...]] = None,
        stroke_weight: Optional[int] = None,
        stroke_width: Optional[int] = None,
        cap: Optional[str] = None,
        join: Optional[str] = None,
    ) -> None:
        """Draw rectangle. Per-call fill/stroke/stroke_weight override global state when provided."""
        # Delegate rectangle drawing to primitives module which centralizes
        # alpha-aware compositing and transform handling.
        return _primitives.rect(self, x, y, w, h, fill=fill, stroke=stroke, stroke_weight=stroke_weight, stroke_width=stroke_width, cap=cap, join=join)

 

    def ellipse(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: Optional[Tuple[int, ...]] = None,
        stroke: Optional[Tuple[int, ...]] = None,
        stroke_weight: Optional[int] = None,
        stroke_width: Optional[int] = None,
        cap: Optional[str] = None,
        join: Optional[str] = None,
    ) -> None:
        """Draw ellipse with optional per-call fill/stroke/weight overrides."""
        return _primitives.ellipse(self, x, y, w, h, fill=fill, stroke=stroke, stroke_weight=stroke_weight, stroke_width=stroke_width, cap=cap, join=join)

    def circle(
        self,
        x: float,
        y: float,
        d: float,
        fill: Optional[tuple[int, ...]] = None,
        stroke: Optional[tuple[int, ...]] = None,
        stroke_weight: Optional[int] = None,
        stroke_width: Optional[int] = None,
        cap: Optional[str] = None,
        join: Optional[str] = None,
    ) -> None:
        """Convenience wrapper to draw a circle with diameter `d`. Forwards to ellipse()."""
        # diameter used as both width and height — delegate to primitives
        return _primitives.circle(self, x, y, d, fill=fill, stroke=stroke, stroke_weight=stroke_weight, stroke_width=stroke_width, cap=cap, join=join)

    # Backwards-compatible alias: `img` -> `image`
    def img(self, *args, **kwargs) -> None:
        """Compatibility alias matching some examples that call `img(...)` on surfaces."""
        return self.image(*args, **kwargs)

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    color: ColorTupleOrNone = None,
        width: Optional[int] = None,
    # compatibility aliases
    stroke: ColorTupleOrNone = None,
        stroke_width: Optional[int] = None,
        cap: Optional[str] = None,
        join: Optional[str] = None,
    ) -> None:
        """Draw a line segment. If `color` or `width` are None the surface's
        current stroke and stroke_weight are used. Optional `cap` and `join`
        temporarily override line cap/join styles for this draw call.
        """
        # Delegate line drawing to primitives which implements alpha-safe
        # stroking and transform handling.
        return _primitives.line(self, x1, y1, x2, y2, color=color, width=width, stroke=stroke, stroke_width=stroke_width, cap=cap, join=join)

    # Convenience shape helpers to mirror Sketch API on Surface so OffscreenSurface
    # supports triangle/quad directly.
    def triangle(self, x1, y1, x2, y2, x3, y3, fill: ColorTupleOrNone = None, stroke: ColorTupleOrNone = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None) -> None:
        return _primitives.triangle(self, x1, y1, x2, y2, x3, y3, fill=fill, stroke=stroke, stroke_weight=stroke_weight, stroke_width=stroke_width)

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4, fill: ColorTupleOrNone = None, stroke: ColorTupleOrNone = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None) -> None:
        return _primitives.quad(self, x1, y1, x2, y2, x3, y3, x4, y4, fill=fill, stroke=stroke, stroke_weight=stroke_weight, stroke_width=stroke_width)

    def arc(self, x: float, y: float, w: float, h: float, start_rad: float, end_rad: float, mode: str = "open", fill: ColorTupleOrNone = None, stroke: ColorTupleOrNone = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None) -> None:
        return _primitives.arc(self, x, y, w, h, start_rad, end_rad, mode=mode, fill=fill, stroke=stroke, stroke_weight=stroke_weight, stroke_width=stroke_width)

    def point(self, x: float, y: float, color: ColorTupleOrNone = None, z: float | None = None) -> None:
        """Draw a point at (x,y).

        - If `color` is provided, use it; otherwise use the current stroke color.
        - `z` is accepted for API compatibility but ignored for the 2D pygame backend.
        - Honors transforms. If `stroke_weight` > 1, draw a small filled circle/rect
          to approximate a thicker point.
        """
        return _primitives.point(self, x, y, color=color, z=z)

    def blit(self, other: pygame.Surface, x: int = 0, y: int = 0) -> None:
        self._surf.blit(other, (int(x), int(y)))

    def blit_image(self, img: object, x: int = 0, y: int = 0) -> None:
        """Blit an image or OffscreenSurface-like object onto this surface.

        Accepts either a pygame.Surface or an object with a `raw` attribute
        returning a pygame.Surface (e.g., `OffscreenSurface`).
        """
        # Backwards-compatible wrapper that delegates to `image`.
        # Kept for existing code; prefer `image()` in new examples.
        self.image(img, x, y)

    def image(self, img: object, x: int = 0, y: int = 0, w: int | None = None, h: int | None = None) -> None:
        """Draw an image or OffscreenSurface-like object onto this surface.

        Signature mirrors Processing's `image(img, x, y, [w, h])`.
        - `img` may be a pygame.Surface or an object exposing `raw` which
          returns a pygame.Surface (e.g., `OffscreenSurface`).
        - If `w` and `h` are provided the source will be scaled using
          pygame.transform.smoothscale before drawing.
        """
        if img is None:
            return
        src = getattr(img, "raw", img)
        # src may be a pygame.Surface or an object exposing `raw`. Statically
        # treat it as a pygame.Surface for typing purposes.
        src_surf: pygame.Surface = src  # type: ignore[assignment]
        # Delegate tint + blend logic to dedicated module for testability and
        # future optimization (blending.py). This mirrors the previous
        # inlined `_blit_with_optional_tint` behavior.
        from pycreative.blending import apply_blit_with_blend

        def _blit_with_optional_tint(surf_to_blit: pygame.Surface, bx: int, by: int) -> None:
            apply_blit_with_blend(self._surf, surf_to_blit, bx, by, self._blend_mode, tint=self._tint)

        if self._is_identity_transform():
            # Interpret x,y according to image_mode
            if self._image_mode == self.MODE_CENTER:
                # center: x,y represent center of drawn image
                if w is None or h is None:
                    iw, ih = src_surf.get_size() if hasattr(src_surf, "get_size") else (src_surf.get_width(), src_surf.get_height())
                else:
                    iw, ih = int(w), int(h)
                bx = int(x - iw / 2)
                by = int(y - ih / 2)
                if w is None or h is None:
                    _blit_with_optional_tint(src_surf, bx, by)
                else:
                    scaled = pygame.transform.smoothscale(src_surf, (int(w), int(h)))
                    _blit_with_optional_tint(scaled, bx, by)
            elif self._image_mode == self.MODE_CORNERS:
                # Interpret (x,y,w,h) as (x1,y1,x2,y2)
                if w is None or h is None:
                    # fallback to CORNER behavior
                    bx = int(x)
                    by = int(y)
                    if w is None or h is None:
                        _blit_with_optional_tint(src_surf, bx, by)
                else:
                    x1 = int(x)
                    y1 = int(y)
                    x2 = int(w)
                    y2 = int(h)
                    left = min(x1, x2)
                    top = min(y1, y2)
                    width = abs(x2 - x1)
                    height = abs(y2 - y1)
                    if width == 0 or height == 0:
                        return
                    scaled = pygame.transform.smoothscale(src_surf, (width, height))
                    _blit_with_optional_tint(scaled, left, top)
            else:
                # default CORNER: x,y represent top-left
                bx = int(x)
                by = int(y)
                if w is None or h is None:
                    _blit_with_optional_tint(src_surf, bx, by)
                else:
                    scaled = pygame.transform.smoothscale(src_surf, (int(w), int(h)))
                    _blit_with_optional_tint(scaled, bx, by)
        else:
            # Simple image transform support: handle translation + uniform scale + rotation via rotozoom
            # Attempt to detect uniform scale from current matrix; fall back to blit at transformed origin.
            sx, sy = decompose_scale(self._current_matrix())
            avg_scale = (sx + sy) / 2.0 if sx > 0 and sy > 0 else 1.0
            # compute transformed origin
            tx, ty = self._transform_point(x, y)
            try:
                if w is None or h is None:
                    img_surf = src_surf
                else:
                    img_surf = pygame.transform.smoothscale(src_surf, (int(w), int(h)))
                # use rotozoom for rotation+scale; angle extraction is approximate
                # compute angle from matrix using arctan2 of first column
                import math

                a = self._current_matrix()[0][0]
                b = self._current_matrix()[1][0]
                angle = math.degrees(math.atan2(b, a))
                transformed = pygame.transform.rotozoom(img_surf, -angle, avg_scale)
                # rotozoom rotates around center; blit centered at transformed center
                rect = transformed.get_rect()
                # adjust for rotation/scaling centering
                self._surf.blit(transformed, (int(tx - rect.width / 2), int(ty - rect.height / 2)))
            except Exception:
                # fallback: simple blit at transformed origin
                self._surf.blit(src_surf, (int(tx), int(ty)))
        

    def polygon(self, points: list[tuple[float, float]]) -> None:
        return _primitives.polygon(self, points)

    def polygon_with_style(self, points: list[tuple[float, float]], fill: ColorTupleOrNone = None, stroke: ColorTupleOrNone = None, stroke_weight: Optional[int] = None, cap: Optional[str] = None, join: Optional[str] = None) -> None:
        return _primitives.polygon_with_style(self, points, fill=fill, stroke=stroke, stroke_weight=stroke_weight, cap=cap, join=join)

    # --- shape construction helpers (beginShape/vertex/endShape) ---
    def begin_shape(self, mode: str | None = None) -> None:
        """Start collecting vertices for a custom shape (beginShape in Processing).

        mode may be one of: None (default polygon/polyline), 'POINTS', 'LINES',
        'TRIANGLES', 'TRIANGLE_FAN', 'TRIANGLE_STRIP', 'QUADS', 'QUAD_STRIP'.
        """
        self._shape_points = []
        try:
            self._shape_mode = None if mode is None else str(mode).upper()
        except Exception:
            self._shape_mode = None

    def vertex(self, x: float, y: float) -> None:
        """Add a vertex to the current shape under construction.

        This stores a typed entry so shape builders can include curve segments
        (bezier) along with straight vertices.
        """
        self._shape_points.append(("v", (x, y)))

    def bezier_vertex(self, cx1: float, cy1: float, cx2: float, cy2: float, x3: float, y3: float) -> None:
        """Add a cubic bezier segment to the current shape.

        The bezier segment uses the previous vertex in the buffer as the
        starting point (p0), the two control points (cx1,cy1) and (cx2,cy2),
        and (x3,y3) as the endpoint (p3). During `end_shape()` these segments
        are flattened to many small line segments to allow filling/stroking.
        """
        self._shape_points.append(("bz", (cx1, cy1, cx2, cy2, x3, y3)))

    # compatibility alias (Processing-style)
    bezierVertex = bezier_vertex


    def end_shape(self, close: bool = False) -> None:
        """Finish the current shape and draw it.

        If `close` is True the shape is closed (polygon), otherwise it's drawn
        as an open polyline.
        """
        if not self._shape_points:
            return

        # Expand the typed shape buffer into a flat list of points. If bezier
        # segments are present we sample them at a fixed resolution to produce
        # a list of straight segments suitable for pygame polygon/lines.
        pts: list[tuple[float, float]] = []
        prev_pt: tuple[float, float] | None = None
        for entry in self._shape_points:
            tag, data = entry
            if tag == "v":
                x, y = data
                pts.append((x, y))
                prev_pt = (x, y)
            elif tag == "bz":
                # data: (cx1, cy1, cx2, cy2, x3, y3)
                if prev_pt is None:
                    # no starting point to attach to; skip
                    continue
                cx1, cy1, cx2, cy2, x3, y3 = data
                p0x, p0y = prev_pt
                samples = self._flatten_cubic_bezier((p0x, p0y), (cx1, cy1), (cx2, cy2), (x3, y3), steps=20)
                # samples includes start point; omit first to avoid duplicate
                for s in samples[1:]:
                    pts.append(s)
                prev_pt = (x3, y3)

        if not pts:
            self._shape_points = []
            return

        mode = getattr(self, "_shape_mode", None)

        # Note: do not pre-apply transforms here. Primitives are responsible
        # for applying the current transform (when appropriate) to ensure a
        # single, consistent transform pass. Applying transforms twice can
        # move vertices off their intended positions.

        def draw_poly(p):
            # helper: draw polygon/triangle/quad using existing polygon helper
            if p:
                self.polygon(p)

        if mode is None:
            # default: polygon when closed else polyline
            if close:
                self.polygon(pts)
            else:
                self.polyline(pts)
        elif mode == "POINTS":
            # draw single points (use stroke color if available else fill)
            color = self._stroke if self._stroke is not None else self._fill
            if color is not None:
                r = max(1, int(self._stroke_weight))
                for x, y in pts:
                    pygame.draw.circle(self._surf, color, (int(x), int(y)), r)
        elif mode == "LINES":
            color = self._stroke if self._stroke is not None else self._fill
            w = int(self._stroke_weight)
            for i in range(0, len(pts) - 1, 2):
                a = pts[i]
                b = pts[i + 1]
                if color is not None and w > 0:
                    pygame.draw.line(self._surf, color, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), w)
        elif mode == "TRIANGLES":
            for i in range(0, len(pts) - 2, 3):
                tri = [pts[i], pts[i + 1], pts[i + 2]]
                draw_poly(tri)
        elif mode == "TRIANGLE_FAN":
            if len(pts) >= 3:
                c = pts[0]
                for i in range(1, len(pts) - 1):
                    tri = [c, pts[i], pts[i + 1]]
                    draw_poly(tri)
        elif mode == "TRIANGLE_STRIP":
            for i in range(0, len(pts) - 2):
                if i % 2 == 0:
                    tri = [pts[i], pts[i + 1], pts[i + 2]]
                else:
                    tri = [pts[i + 1], pts[i], pts[i + 2]]
                draw_poly(tri)
        elif mode == "QUADS":
            for i in range(0, len(pts) - 3, 4):
                quad = [pts[i], pts[i + 1], pts[i + 2], pts[i + 3]]
                draw_poly(quad)
        elif mode == "QUAD_STRIP":
            # quad strip uses pairs: (v0,v1,v2,v3) -> quad(v0,v1,v3,v2)
            for i in range(0, len(pts) - 3, 2):
                quad = [pts[i], pts[i + 1], pts[i + 3], pts[i + 2]]
                draw_poly(quad)
        else:
            # unknown mode: fallback to polygon/polyline
            if close:
                self.polygon(pts)
            else:
                self.polyline(pts)

        # clear buffer
        self._shape_points = []

    def _flatten_cubic_bezier(self, p0: tuple[float, float], p1: tuple[float, float], p2: tuple[float, float], p3: tuple[float, float], steps: int = 16) -> list[tuple[float, float]]:
        # Delegate to shape_math.flatten_cubic_bezier for the implementation.
        return flatten_cubic_bezier(p0, p1, p2, p3, steps=steps)

    # --- bezier helpers (Processing-like) ---
    def bezier_detail(self, steps: int) -> None:
        """Set the default sampling resolution used by `bezier()` and
        when flattening bezier segments in `end_shape()`.
        """
        self._bezier_detail = max(2, int(steps))

    def bezier(self, x1: float, y1: float, cx1: float, cy1: float, cx2: float, cy2: float, x2: float, y2: float) -> None:
        """Draw a cubic bezier curve from (x1,y1) to (x2,y2) with control
        points (cx1,cy1) and (cx2,cy2). This renders using `polyline()` and
        respects stroke settings only (matching Processing's bezier behavior).
        """
        samples = self._flatten_cubic_bezier((x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2), steps=self._bezier_detail)
        # Draw as an open polyline; polyline handles stroke/stroke_weight
        self.polyline(samples)

    def bezier_point(self, p0, p1, p2, p3, t: float):
        """Evaluate a cubic bezier at parameter t in [0,1].

        The function accepts scalar coordinates or 2D tuples. If scalars are
        passed it returns a scalar; if tuples are passed it returns a tuple.
        """
        return bezier_point(p0, p1, p2, p3, t)

    def bezier_tangent(self, p0, p1, p2, p3, t: float):
        """Compute the derivative (tangent) of the cubic bezier at parameter t.

        Returns a scalar for scalar inputs or a tuple (dx, dy) for 2D inputs.
        """
        return bezier_tangent(p0, p1, p2, p3, t)

    # --- curve helpers (Catmull-Rom / Processing-style) ---
    def curve_detail(self, steps: int) -> None:
        """Set sampling resolution used by `curve()` when flattening into line segments."""
        self._curve_detail = max(2, int(steps))

    def curve_tightness(self, tightness: float) -> None:
        """Set the curve tightness (0.0 = Catmull-Rom default). Higher values reduce tangents."""
        try:
            self._curve_tightness = float(tightness)
        except Exception:
            return

    def curve_point(self, p0, p1, p2, p3, t: float):
        """Evaluate a Catmull-Rom-like curve (Hermite form) at parameter t in [0,1].

        Accepts scalar coordinates or 2D tuples. Uses p1 and p2 as endpoints and
        constructs tangents from p0/p2 and p1/p3 scaled by (1 - tightness)/2.
        """
        return curve_point(p0, p1, p2, p3, t, tightness=self._curve_tightness)

    def curve_tangent(self, p0, p1, p2, p3, t: float):
        """Compute tangent (derivative) of the curve at parameter t.

        Returns scalar or 2-tuple depending on input.
        """
        return curve_tangent(p0, p1, p2, p3, t, tightness=self._curve_tightness)

    def curve(self, x0: float, y0: float, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> None:
        """Draw a Catmull-Rom-like curve from (x1,y1) to (x2,y2) with (x0,y0) and (x3,y3) as neighboring points.

        The curve is flattened into straight segments using `curve_detail`.
        Only stroke is respected (matching Processing semantics).
        """
        pts: list[tuple[float, float]] = []
        steps = max(2, int(self._curve_detail))
        for i in range(steps + 1):
            t = i / steps
            p = self.curve_point((x0, y0), (x1, y1), (x2, y2), (x3, y3), t)
            pts.append(p)
        # draw as open polyline
        self.polyline(pts)

    def polyline(self, points: list[tuple[float, float]]) -> None:
        # default simple wrapper uses the current stroke/weight — delegate
        return _primitives.polyline(self, points)

    def polyline_with_style(self, points: list[tuple[float, float]], stroke: ColorTupleOrNone = None, stroke_weight: Optional[int] = None, cap: Optional[str] = None, join: Optional[str] = None) -> None:
        """Draw an open polyline connecting the sequence of points with optional per-call styling."""
        if not points:
            return
        prev_cap = self._line_cap
        prev_join = self._line_join
        prev_stroke = self._stroke
        prev_sw = self._stroke_weight
        try:
            if cap is not None:
                self.set_line_cap(cap)
            if join is not None:
                self.set_line_join(join)
            if stroke is not None:
                # coerce stroke color similarly to other helpers
                try:
                    if isinstance(stroke, Color):
                        self._stroke = self._coerce_input_color(stroke)
                    else:
                        self._stroke = self._coerce_input_color(stroke)
                except Exception:
                    self._stroke = stroke
            if stroke_weight is not None:
                try:
                    self._stroke_weight = int(stroke_weight)
                except Exception:
                    pass
            return _primitives.polyline(self, points)
        finally:
            self._line_cap = prev_cap
            self._line_join = prev_join
            self._stroke = prev_stroke
            self._stroke_weight = prev_sw

        # NOTE:
        # The cap and join handling here is intentionally lightweight and approximate.
        # - We emulate 'round' caps/joins by stamping circles at endpoints/vertices.
        # - 'butt' and 'square' rely on pygame's default rendering behavior and are not
        #   specially constructed here.
        # Full, pixel-accurate miter/bevel handling requires explicit geometry (miter
        # joins, miter-limit calculation, and potentially polygon-based stroking)
        # or a renderer that exposes native cap/join controls. Implementing full
        # miter math is deferred to a follow-up task (see T503 in specs/dev-refactor/tasks.md).

    def set_line_cap(self, cap: str) -> None:
        """Set line cap style: 'butt', 'round', or 'square'."""
        if cap in ("butt", "round", "square"):
            self._line_cap = cap

    def set_line_join(self, join: str) -> None:
        """Set line join style: 'miter', 'round', or 'bevel'."""
        if join in ("miter", "round", "bevel"):
            self._line_join = join

    # --- style state helpers (public API) ---
    def fill(self, color: Optional[tuple[int, ...]]) -> None:
        """Set the fill color. Use `None` to disable filling (noFill())."""
        if color is None:
            self._fill = None
            return
        # Accept Color instances directly
        if isinstance(color, Color):
            try:
                self._fill = color.to_rgba_tuple()
            except Exception:
                self._fill = color.to_tuple()
            return

        # Interpret tuples according to current color mode, using Color helpers
        try:
            mode, m1, _m2, _m3, *_rest = self._color_mode
        except Exception:
            mode, m1, _m2, _m3 = ("RGB", 255, 255, 255)

        try:
            if mode == "HSB" and hasattr(color, "__iter__"):
                vals = list(color)
                h, s, v = vals[0], vals[1], vals[2]
                ma = int(self._color_mode[4]) if len(self._color_mode) >= 5 else m1
                col = Color.from_hsb(h, s, v, max_h=m1, max_s=_m2, max_v=_m3, max_a=ma)
                if len(vals) >= 4:
                    a = int(vals[3]) & 255
                    self._fill = (col.r, col.g, col.b, a)
                else:
                    self._fill = col.to_tuple()
                # apply immediately to underlying surface as a convenience so
                # calling `surface.fill(...)` paints the surface (tests/examples
                # expect this behavior). Wrap in try/except to be best-effort.
                try:
                    self._surf.fill(self._fill)
                except Exception:
                    pass
                return
            # otherwise treat as RGB (values may be in a custom max range)
            if hasattr(color, "__iter__"):
                vals = list(color)
                # Support shorthand grayscale + alpha: (v, a) -> (v,v,v,a)
                if len(vals) == 2:
                    v = vals[0]
                    a = int(vals[1]) & 255
                    col = Color.from_rgb(v, v, v, max_value=m1)
                    self._fill = (col.r, col.g, col.b, a)
                else:
                    r, g, b = vals[0], vals[1], vals[2]
                    col = Color.from_rgb(r, g, b, max_value=m1)
                    if len(vals) >= 4:
                        a = int(vals[3]) & 255
                        self._fill = (col.r, col.g, col.b, a)
                    else:
                        self._fill = col.to_tuple()
                try:
                    self._surf.fill(self._fill)
                except Exception:
                    pass
                return
        except Exception:
            # best-effort: ignore invalid input
            self._fill = None

    def color_mode(self, mode: Optional[str] = None, max1: int = 255, max2: int = 255, max3: int = 255, max4: int | None = None):
        """Get or set the current color mode.

        - color_mode() -> returns a tuple (mode, max1, max2, max3)
        - color_mode('HSB', 255,255,255) -> sets HSB interpretation for future fill()/stroke() calls
        """
        if mode is None:
            return self._color_mode
        try:
            m = str(mode).upper()
            if m in ("RGB", "HSB"):
                a_max = int(max4) if max4 is not None else int(max1)
                self._color_mode = (m, int(max1), int(max2), int(max3), a_max)
        except Exception:
            pass
        return None

    def no_fill(self) -> None:
        """Disable filling for subsequent shape draws."""
        self._fill = None

    def stroke(self, *args) -> None:
        """Set the stroke color. Accepts Processing-style arguments like
        stroke(r, g, b), stroke((r,g,b)), stroke(None) to disable.
        """
        # Normalize incoming args into a single color-like value
        if len(args) == 0:
            return
        if len(args) == 1:
            color_in = args[0]
        else:
            color_in = tuple(args)

        if color_in is None:
            self._stroke = None
            return

        # Prefer the general coercion helper which understands Numbers, tuples,
        # HSB/RGB modes and Color instances.
        try:
            coerced = self._coerce_input_color(color_in)
            self._stroke = tuple(coerced) if coerced is not None else None  # type: ignore[assignment]
            return
        except Exception:
            # Fallback: best-effort handling similar to prior behavior
            try:
                if isinstance(color_in, Color):
                    try:
                        self._stroke = tuple(color_in.to_rgba_tuple())  # type: ignore[assignment]
                    except Exception:
                        self._stroke = tuple(color_in.to_tuple())  # type: ignore[assignment]
                    return
                # last resort: try treating as iterable RGB(A)
                if hasattr(color_in, "__iter__"):
                    vals = list(color_in)
                    r, g, b = vals[0], vals[1], vals[2]
                    col = Color.from_rgb(r, g, b, max_value=self._color_mode[1] if isinstance(self._color_mode, tuple) else 255)
                    if len(vals) >= 4:
                        a = int(vals[3]) & 255
                        self._stroke = (col.r, col.g, col.b, a)
                    else:
                        self._stroke = tuple(col.to_tuple())  # type: ignore[assignment]
                    return
            except Exception:
                self._stroke = None

    def no_stroke(self) -> None:
        """Disable stroke for subsequent shape draws."""
        self._stroke = None

    def stroke_weight(self, w: int) -> None:
        """Set the stroke weight (line width) for subsequent shapes."""
        try:
            self._stroke_weight = int(w)
        except Exception:
            # ignore invalid values
            pass

    @contextmanager
    def style(self, fill: object = ... , stroke: object = ... , stroke_weight: object = ... , cap: object = ... , join: object = ...):
        """Temporarily override drawing style state inside a `with` block.

        Usage:
            with surface.style(fill=None):  # disable fill for block
                surface.rect(...)

        Passing `...` (ellipsis, the default) means "don't change this value".
        To explicitly disable fill or stroke pass `None`.
        """
        prev_fill = self._fill
        prev_stroke = self._stroke
        prev_sw = self._stroke_weight
        prev_cap = self._line_cap
        prev_join = self._line_join
        try:
            if fill is not ...:
                if fill is None:
                    self.no_fill()
                else:
                    # Set _fill directly to avoid clearing the surface when
                    # using the style context manager.
                    if isinstance(fill, Color):
                        try:
                            self._fill = fill.to_rgba_tuple()
                        except Exception:
                            self._fill = fill.to_tuple()
                    else:
                        try:
                            mode, m1, _m2, _m3, *_rest = self._color_mode
                        except Exception:
                            mode, m1, _m2, _m3 = ("RGB", 255, 255, 255)
                        try:
                            if mode == "HSB" and hasattr(fill, "__iter__"):
                                vals = list(fill)
                                h, s, v = vals[0], vals[1], vals[2]
                                ma = int(self._color_mode[4]) if len(self._color_mode) >= 5 else m1
                                col = Color.from_hsb(h, s, v, max_h=m1, max_s=_m2, max_v=_m3, max_a=ma)
                                if len(vals) >= 4:
                                    a = int(vals[3]) & 255
                                    self._fill = (col.r, col.g, col.b, a)
                                else:
                                    self._fill = col.to_tuple()
                            elif hasattr(fill, "__iter__"):
                                vals = list(fill)
                                r, g, b = vals[0], vals[1], vals[2]
                                col = Color.from_rgb(r, g, b, max_value=m1)
                                if len(vals) >= 4:
                                    a = int(vals[3]) & 255
                                    self._fill = (col.r, col.g, col.b, a)
                                else:
                                    self._fill = col.to_tuple()
                            else:
                                self._fill = None
                        except Exception:
                            self._fill = None
            if stroke is not ...:
                if stroke is None:
                    self.no_stroke()
                else:
                    self.stroke(stroke)
            if stroke_weight is not ...:
                from typing import cast

                try:
                    self.stroke_weight(int(cast(int, stroke_weight)))
                except Exception:
                    # ignore invalid stroke weight values
                    pass
            if cap is not ...:
                # only accept string caps
                if isinstance(cap, str):
                    self.set_line_cap(cap)
            if join is not ...:
                if isinstance(join, str):
                    self.set_line_join(join)
            yield self
        finally:
            # restore previous style state
            self._fill = prev_fill
            self._stroke = prev_stroke
            self._stroke_weight = prev_sw
            self._line_cap = prev_cap
            self._line_join = prev_join

    def stroke_path(self, points: list[tuple[float, float]], closed: bool = False, cap: Optional[str] = None, join: Optional[str] = None, miter_limit: float = 10.0) -> None:
        """Unified stroking method that honors cap/join/miter options.

        This is the central API we expect to implement fully later. For now it
        temporarily applies cap/join settings and delegates to `polyline` or
        `polygon` as appropriate.

        TODO: implement geometry-based stroking for accurate miters/bevels
        and a configurable miter limit for performance/quality trade-offs.
        """
        if not points:
            return

        prev_cap = self._line_cap
        prev_join = self._line_join
        try:
            if cap is not None:
                self.set_line_cap(cap)
            if join is not None:
                self.set_line_join(join)

            if closed:
                # draw as polygon (filled/stroked)
                self.polygon(points)
            else:
                self.polyline(points)
        finally:
            # restore previous styles
            self._line_cap = prev_cap
            self._line_join = prev_join


    # --- pixel helpers (copy-based) ---
    def get_pixels(self) -> Any:
        """Return a copy of the surface pixel array as (H, W, C) uint8.

        Delegates to `pycreative.pixels.get_pixels` for the implementation so
        the pixel helpers can be optimized or replaced independently.
        """
        return get_pixels(self._surf)

    def set_pixels(self, arr: Any) -> None:
        """Write a (H,W,3) or (H,W,4) array into the surface.

        Delegates to `pycreative.pixels.set_pixels`.
        """
        return set_pixels(self._surf, arr)

    def get_pixel(self, x: int, y: int) -> Tuple[int, ...]:
        """Return a single pixel color tuple (RGB) or (RGBA). Delegates to `pixels.get_pixel`."""
        return get_pixel(self._surf, x, y)

    def set_pixel(self, x: int, y: int, color: ColorTuple) -> None:
        """Set a single pixel color. Accepts (r,g,b) or (r,g,b,a). Delegates to `pixels.set_pixel`."""
        return set_pixel(self._surf, x, y, color)

    # --- PImage-style pixel helpers ---
    @contextmanager
    def pixels(self):
        """Context manager for pixel access. Yields a `PixelView` and writes
        the data back to the surface on exit.

        Usage:
            with surface.pixels() as pv:
                pv[y,x] = (r,g,b)
        """
        # Delegate to the pixels module context manager which performs a
        # copy-on-enter and writes back on exit.
        with pixels_ctx(self._surf) as pv:
            yield pv

    def load_pixels(self) -> Any:
        """Compatibility shim: returns a PixelView copy of the surface pixels."""
        return self.get_pixels()

    def update_pixels(self, arr: Any) -> None:
        """Compatibility shim: write pixels back to the surface.

        Requires an array or PixelView argument.
        """
        if arr is None:
            raise ValueError("update_pixels requires a pixel array or PixelView")
        self.set_pixels(arr)

    def get(self, *args):
        """PImage-style get().

        - get() -> OffscreenSurface (copy of whole image)
        - get(x,y) -> color tuple (r,g,b) or (r,g,b,a)
        - get(x,y,w,h) -> OffscreenSurface (clipped region)
        """
        if len(args) == 0:
            return OffscreenSurface(self._surf.copy())

        if len(args) == 2:
            x, y = int(args[0]), int(args[1])
            w, h = self._surf.get_size()
            if x < 0 or y < 0 or x >= w or y >= h:
                # Out-of-bounds: return black (with alpha if supported)
                if bool(self._surf.get_flags() & pygame.SRCALPHA):
                    return (0, 0, 0, 0)
                return (0, 0, 0)
            return self.get_pixel(x, y)

        if len(args) == 4:
            x, y, rw, rh = map(int, args)
            sw, sh = self._surf.get_size()
            # Clip to surface bounds
            ix1 = max(0, x)
            iy1 = max(0, y)
            ix2 = min(sw, x + rw)
            iy2 = min(sh, y + rh)
            iw = max(0, ix2 - ix1)
            ih = max(0, iy2 - iy1)
            flags = pygame.SRCALPHA if (self._surf.get_flags() & pygame.SRCALPHA) else 0
            new = pygame.Surface((max(0, iw), max(0, ih)), flags)
            if iw > 0 and ih > 0:
                new.blit(self._surf, (0, 0), pygame.Rect(ix1, iy1, iw, ih))
            return OffscreenSurface(new)

        raise TypeError("get() accepts 0, 2, or 4 arguments")

    def copy(self, *args) -> None:
        """PImage-style copy.

        Signatures:
          - copy() -> returns self (no-op)
          - copy(sx, sy, sw, sh, dx, dy, dw, dh)
          - copy(src_surface, sx, sy, sw, sh, dx, dy, dw, dh)
        """
        # copy() -> return self (Processing returns PImage)
        if len(args) == 0:
            return None

        # copy from other surface: first arg is source
        if len(args) == 9:
            src = args[0]
            try:
                sx, sy, sw, sh, dx, dy, dw, dh = map(int, args[1:9])
            except Exception:
                raise TypeError("copy(src, sx, sy, sw, sh, dx, dy, dw, dh) expects integer coords")
            src_surf = getattr(src, "raw", src)
        elif len(args) == 8:
            try:
                sx, sy, sw, sh, dx, dy, dw, dh = map(int, args)
            except Exception:
                raise TypeError("copy(sx, sy, sw, sh, dx, dy, dw, dh) expects integer coords")
            src_surf = self._surf
        else:
            raise TypeError("copy() signature not recognized")

        # Clip source rect to source surface
        ssw, ssh = src_surf.get_size()
        sx1 = max(0, sx)
        sy1 = max(0, sy)
        sx2 = min(ssw, sx + sw)
        sy2 = min(ssh, sy + sh)
        real_sw = max(0, sx2 - sx1)
        real_sh = max(0, sy2 - sy1)

        if real_sw == 0 or real_sh == 0:
            # nothing to copy
            return None

        # Extract the source region into a temporary surface
        tmp_flags = pygame.SRCALPHA if (src_surf.get_flags() & pygame.SRCALPHA) else 0
        tmp = pygame.Surface((real_sw, real_sh), tmp_flags)
        tmp.blit(src_surf, (0, 0), pygame.Rect(sx1, sy1, real_sw, real_sh))

        # Scale if necessary
        if (real_sw, real_sh) != (dw, dh):
            try:
                tmp = pygame.transform.smoothscale(tmp, (dw, dh))
            except Exception:
                tmp = pygame.transform.scale(tmp, (dw, dh))

    # Blit into destination (self._surf)
        try:
            self._surf.blit(tmp, (dx, dy))
        except Exception as e:
            raise RuntimeError(f"copy failed: {e}")

    def copy_to(self, dest: "Surface", sx: int, sy: int, sw: int, sh: int, dx: int, dy: int, dw: int, dh: int) -> None:
        """Copy a rect from this surface into `dest`.

        Convenience wrapper which makes image-like objects able to copy
        their pixels into another surface without the caller needing to
        call the destination's copy signature. Example:
            img.copy_to(self.surface, sx, sy, sw, sh, dx, dy, dw, dh)
        """
        # Delegate to the destination Surface.copy using this surface as src
        dest.copy(self, sx, sy, sw, sh, dx, dy, dw, dh)
        return None

    def set(self, x: int, y: int, value) -> None:
        """PImage-style set. If `value` is a color tuple, set a single pixel.
        If `value` is an image/surface-like, blit it with upper-left at (x,y).
        """
        w, h = self._surf.get_size()
        if isinstance(value, (tuple, list)):
            # Single pixel set
            if x < 0 or y < 0 or x >= w or y >= h:
                # Write a helpful hint to console, but don't raise
                print(f"set: pixel ({x},{y}) out of bounds for surface size {(w,h)}")
                return
            # Clamp values and set
            try:
                if len(value) == 4:
                    self._surf.set_at((int(x), int(y)), (int(value[0]) & 255, int(value[1]) & 255, int(value[2]) & 255, int(value[3]) & 255))
                else:
                    self._surf.set_at((int(x), int(y)), (int(value[0]) & 255, int(value[1]) & 255, int(value[2]) & 255))
            except Exception as e:
                raise RuntimeError(f"set pixel failed: {e}")
            return

        # If value is surface-like, delegate to image() which handles scaling/clipping
        src = getattr(value, "raw", value)
        try:
            self.image(src, int(x), int(y))
        except Exception as e:
            raise RuntimeError(f"set image failed: {e}")


class OffscreenSurface(Surface):
    """Offscreen surface wrapper which mirrors Surface API and provides
    context-manager helpers and small utilities like save/get_image.

    This intentionally reuses the same drawing primitives as Surface so
    code that draws to the main canvas can draw to an offscreen buffer
    without changes.
    """

    def __init__(self, surf: pygame.Surface) -> None:
        super().__init__(surf)

    def __enter__(self) -> "OffscreenSurface":
        # Context manager entry — no global state to swap for now.
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        # Nothing special to clean up; provided for convenience.
        return None

    def save(self, path: str) -> None:
        """Save the underlying surface to a file using pygame.image.save."""
        try:
            pygame.image.save(self._surf, path)
        except Exception:
            # best-effort; don't raise during examples
            print(f"Failed to save offscreen surface to {path}")


    # --- text/image helpers ---
    def text(self, txt: str, x: int, y: int, font_name: Optional[str] = None, size: int = 24, color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        font = pygame.font.SysFont(font_name, int(size))
        surf = font.render(str(txt), True, color)
        self._surf.blit(surf, (int(x), int(y)))

    def load_image(self, path: str) -> pygame.Surface:
        return pygame.image.load(path)

    def blit_image(self, img: object, x: int = 0, y: int = 0) -> None:
        # Delegate to the unified `image` API (keeps compatibility)
        self.image(img, int(x), int(y))

    def polygon(self, points: list[tuple[float, float]]) -> None:
        # Delegate to the alpha-aware polygon_with_style implementation so
        # OffscreenSurface shares the same compositing behavior as Surface
        # (handles HSB/color coercion and temp-SRCALPHA blitting when alpha is present).
        self.polygon_with_style(points, fill=self._fill, stroke=self._stroke, stroke_weight=self._stroke_weight)
