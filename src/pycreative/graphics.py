from __future__ import annotations

from typing import Optional, Tuple

import pygame
from typing import Any
from contextlib import contextmanager

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


# NOTE: numpy support removed — pixel helpers use pure-Python nested lists.
_HAS_NUMPY = False
_np = None


class PixelView:
    """Thin adapter around either a numpy array or a nested list that provides
    uniform (h,w,c) indexing and a 'shape' attribute. This keeps sketches
    from needing to import numpy directly while preserving fast paths.
    """
    def __init__(self, data: Any):
        self._data = data

    @property
    def shape(self):
        if hasattr(self._data, "shape"):
            return self._data.shape
        h = len(self._data)
        w = len(self._data[0]) if h > 0 else 0
        c = len(self._data[0][0]) if w > 0 else 0
        return (h, w, c)

    def __getitem__(self, idx):
        # Support numpy-style multi-indexing like [y, x, c] when _data is nested lists
        if isinstance(idx, tuple):
            # drill down through nested lists
            cur = self._data
            for k in idx:
                cur = cur[k]
            return cur
        return self._data[idx]

    def __setitem__(self, idx, value):
        # Support multi-index assignment arr[y, x, c] for nested-lists
        if isinstance(idx, tuple):
            cur = self._data
            # traverse to last container
            for k in idx[:-1]:
                cur = cur[k]
            cur[idx[-1]] = value
            return
        self._data[idx] = value

    def raw(self):
        return self._data


class Surface:
    """Lightweight wrapper around a pygame.Surface exposing primitives and
    simple drawing state (fill, stroke, stroke weight) and modes.

    - ellipse(x, y, w, h): x,y are center by default
    - rect accepts CORNER (x,y top-left) or CENTER modes
    """

    MODE_CORNER = "CORNER"
    MODE_CENTER = "CENTER"

    def __init__(self, surf: pygame.Surface) -> None:
        self._surf = surf
        # Drawing state
        self._fill: Optional[Tuple[int, int, int]] = (255, 255, 255)
        self._stroke: Optional[Tuple[int, int, int]] = None
        self._stroke_weight: int = 1
        self._rect_mode: str = self.MODE_CORNER
        self._ellipse_mode: str = self.MODE_CENTER
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
        # Color mode: ('RGB'|'HSB', max1, max2, max3)
        # Defaults mirror common 0-255 ranges. When in HSB mode, fill()/stroke()
        # will interpret tuple inputs as (h,s,b) in the configured ranges.
        self._color_mode: tuple[str, int, int, int] = ("RGB", 255, 255, 255)

    # --- transform stack helpers ---
    def _current_matrix(self):
        return self._matrix_stack[-1]

    def push(self) -> None:
        """Push a copy of the current transform onto the stack."""
        top = self._current_matrix()
        self._matrix_stack.append([row[:] for row in top])

    def pop(self) -> None:
        """Pop the top transform. The base identity matrix cannot be popped."""
        if len(self._matrix_stack) == 1:
            raise IndexError("cannot pop base transform")
        self._matrix_stack.pop()

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

    def _transform_point(self, x: float, y: float) -> tuple[float, float]:
        return transform_point(self._current_matrix(), x, y)


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
        if mode in (self.MODE_CORNER, self.MODE_CENTER):
            self._rect_mode = mode
        return None

    def ellipse_mode(self, mode: str | None = None) -> str | None:
        """Get or set ellipse mode. Call with no args to get current mode,
        or pass `Surface.MODE_CORNER` / `Surface.MODE_CENTER` to set it.
        """
        if mode is None:
            return self._ellipse_mode
        if mode in (self.MODE_CORNER, self.MODE_CENTER):
            self._ellipse_mode = mode
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
        # Accept Color instances directly
        try:
            if isinstance(color, Color):
                self._surf.fill(color.to_tuple())
                return
        except Exception:
            pass

        # If HSB color mode is active and a 3-tuple is provided interpret as HSB
        try:
            mode, m1, m2, m3 = self._color_mode
            if mode == "HSB" and hasattr(color, "__iter__"):
                h, s, v = color
                col = Color.from_hsb(float(h), float(s), float(v), max_value=m1)
                self._surf.fill(col.to_tuple())
                return
        except Exception:
            pass

        # fallback: treat as RGB tuple
        try:
            rgb = (int(color[0]) & 255, int(color[1]) & 255, int(color[2]) & 255)
            self._surf.fill(rgb)
        except Exception:
            # best-effort: ignore invalid input
            return

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill: Optional[Tuple[int, int, int]] = None,
        stroke: Optional[Tuple[int, int, int]] = None,
        stroke_weight: Optional[int] = None,
        stroke_width: Optional[int] = None,
        cap: Optional[str] = None,
        join: Optional[str] = None,
    ) -> None:
        """Draw rectangle. Per-call fill/stroke/stroke_weight override global state when provided."""
        # compute topleft depending on mode
        if self._rect_mode == self.MODE_CENTER:
            tlx = x - w / 2
            tly = y - h / 2
        else:
            tlx = x
            tly = y

        # If no transform is active use the fast path with integers
        if self._is_identity_transform():
            rect = pygame.Rect(int(tlx), int(tly), int(w), int(h))
            draw_polygon = False
        else:
            # transform the four rectangle corners into a polygon
            pts = [
                (tlx, tly),
                (tlx + w, tly),
                (tlx + w, tly + h),
                (tlx, tly + h),
            ]
            pts = transform_points(self._current_matrix(), pts)
            draw_polygon = True

        prev_cap = self._line_cap
        prev_join = self._line_join
        try:
            if cap is not None:
                self.set_line_cap(cap)
            if join is not None:
                self.set_line_join(join)

            # prefer explicit stroke_width alias if provided
            if stroke_width is not None:
                sw = int(stroke_width)
            elif stroke_weight is not None:
                sw = int(stroke_weight)
            else:
                sw = int(self._stroke_weight)

            fill_col = fill if fill is not None else self._fill
            stroke_col = stroke if stroke is not None else self._stroke

            if fill_col is not None:
                if draw_polygon:
                    pygame.draw.polygon(self._surf, fill_col, [(int(px), int(py)) for px, py in pts])
                else:
                    pygame.draw.rect(self._surf, fill_col, rect)
            if stroke_col is not None and sw > 0:
                if draw_polygon:
                    pygame.draw.polygon(self._surf, stroke_col, [(int(px), int(py)) for px, py in pts], sw)
                else:
                    pygame.draw.rect(self._surf, stroke_col, rect, sw)
        finally:
            self._line_cap = prev_cap
            self._line_join = prev_join

 

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
        cap: Optional[str] = None,
        join: Optional[str] = None,
    ) -> None:
        """Draw ellipse with optional per-call fill/stroke/weight overrides."""
        # ellipse mode: center or corner
        if self._ellipse_mode == self.MODE_CENTER:
            cx = x
            cy = y
            rx = w / 2.0
            ry = h / 2.0
        else:
            cx = x + w / 2.0
            cy = y + h / 2.0
            rx = w / 2.0
            ry = h / 2.0

        prev_cap = self._line_cap
        prev_join = self._line_join
        try:
            if cap is not None:
                self.set_line_cap(cap)
            if join is not None:
                self.set_line_join(join)

            # accept both stroke_weight and stroke_width for compatibility;
            # prefer stroke_width if provided by caller.
            if stroke_width is not None:
                sw = int(stroke_width)
            elif stroke_weight is not None:
                sw = int(stroke_weight)
            else:
                sw = int(self._stroke_weight)

            fill_col = fill if fill is not None else self._fill
            stroke_col = stroke if stroke is not None else self._stroke

            if self._is_identity_transform():
                if self._ellipse_mode == self.MODE_CENTER:
                    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
                else:
                    rect = pygame.Rect(int(x), int(y), int(w), int(h))
                if fill_col is not None:
                    pygame.draw.ellipse(self._surf, fill_col, rect)
                if stroke_col is not None and sw > 0:
                    pygame.draw.ellipse(self._surf, stroke_col, rect, sw)
            else:
                # approximate transformed ellipse by sampling points on the ellipse
                import math

                samples = max(24, int(2 * math.pi * max(rx, ry) / 6))
                pts = []
                for i in range(samples):
                    t = (i / samples) * 2 * math.pi
                    px = cx + rx * math.cos(t)
                    py = cy + ry * math.sin(t)
                    pts.append((px, py))
                pts = transform_points(self._current_matrix(), pts)
                int_pts = [(int(px), int(py)) for px, py in pts]
                if fill_col is not None:
                    pygame.draw.polygon(self._surf, fill_col, int_pts)
                if stroke_col is not None and sw > 0:
                    pygame.draw.polygon(self._surf, stroke_col, int_pts, sw)
        finally:
            self._line_cap = prev_cap
            self._line_join = prev_join

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
        color: Optional[Tuple[int, int, int]] = None,
        width: Optional[int] = None,
        # compatibility aliases
        stroke: Optional[Tuple[int, int, int]] = None,
        stroke_width: Optional[int] = None,
        cap: Optional[str] = None,
        join: Optional[str] = None,
    ) -> None:
        """Draw a line segment. If `color` or `width` are None the surface's
        current stroke and stroke_weight are used. Optional `cap` and `join`
        temporarily override line cap/join styles for this draw call.
        """
        # prefer explicit alias arguments if provided
        col = stroke if stroke is not None else (color if color is not None else self._stroke)
        if stroke_width is not None:
            w = int(stroke_width)
        else:
            w = int(width) if width is not None else int(self._stroke_weight)
        if col is None or w <= 0:
            # nothing to draw
            return

        prev_cap = self._line_cap
        prev_join = self._line_join
        try:
            if cap is not None:
                self.set_line_cap(cap)
            if join is not None:
                self.set_line_join(join)

            if self._is_identity_transform():
                pygame.draw.line(self._surf, col, (int(x1), int(y1)), (int(x2), int(y2)), int(w))
            else:
                p1 = self._transform_point(x1, y1)
                p2 = self._transform_point(x2, y2)
                pygame.draw.line(self._surf, col, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), int(w))

            # emulate round caps if requested
            if self._line_cap == "round":
                radius = max(1, int(w / 2))
                pygame.draw.circle(self._surf, col, (int(x1), int(y1)), radius)
                pygame.draw.circle(self._surf, col, (int(x2), int(y2)), radius)

        finally:
            # restore
            self._line_cap = prev_cap
            self._line_join = prev_join

    # Convenience shape helpers to mirror Sketch API on Surface so OffscreenSurface
    # supports triangle/quad directly.
    def triangle(self, x1, y1, x2, y2, x3, y3, fill: Optional[Tuple[int, int, int]] = None, stroke: Optional[Tuple[int, int, int]] = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None) -> None:
        pts = [(x1, y1), (x2, y2), (x3, y3)]
        # prefer stroke_width
        sw = int(stroke_width) if stroke_width is not None else (int(stroke_weight) if stroke_weight is not None else None)
        self.polygon_with_style(pts, fill=fill, stroke=stroke, stroke_weight=sw)

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4, fill: Optional[Tuple[int, int, int]] = None, stroke: Optional[Tuple[int, int, int]] = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None) -> None:
        pts = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        sw = int(stroke_width) if stroke_width is not None else (int(stroke_weight) if stroke_weight is not None else None)
        self.polygon_with_style(pts, fill=fill, stroke=stroke, stroke_weight=sw)

    def arc(self, x: float, y: float, w: float, h: float, start_rad: float, end_rad: float, mode: str = "open", fill: Optional[Tuple[int, int, int]] = None, stroke: Optional[Tuple[int, int, int]] = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None) -> None:
        """Draw an arc; accepts per-call fill/stroke/stroke_weight (or stroke_width) like Sketch.arc."""
        # save previous state
        prev_fill = self._fill
        prev_stroke = self._stroke
        prev_sw = self._stroke_weight
        try:
            if fill is not None:
                self.fill(fill)
            if stroke is not None:
                self.stroke(stroke)
            # prefer stroke_width alias
            if stroke_width is not None:
                self.stroke_weight(int(stroke_width))
            elif stroke_weight is not None:
                self.stroke_weight(int(stroke_weight))
            # delegate to existing implementation (which uses self._fill/_stroke/_stroke_weight)
            # Note: reuse original arc implementation body by calling the internal arc logic
            rect = pygame.Rect(int(x - w / 2), int(y - h / 2), int(w), int(h))
            if mode == "open":
                if self._stroke is not None:
                    pygame.draw.arc(self._surf, self._stroke, rect, float(start_rad), float(end_rad), int(self._stroke_weight))
            else:
                import math

                steps = max(6, int((end_rad - start_rad) * 10))
                pts = []
                cx = x
                cy = y
                rx = w / 2.0
                ry = h / 2.0
                for i in range(steps + 1):
                    t = start_rad + (end_rad - start_rad) * (i / max(1, steps))
                    px = cx + rx * math.cos(t)
                    py = cy + ry * math.sin(t)
                    pts.append((px, py))
                if mode == "pie":
                    poly = [(int(cx), int(cy))] + [(int(px), int(py)) for px, py in pts]
                    if self._fill is not None:
                        pygame.draw.polygon(self._surf, self._fill, poly)
                    if self._stroke is not None and self._stroke_weight > 0:
                        pygame.draw.polygon(self._surf, self._stroke, poly, int(self._stroke_weight))
                elif mode == "chord":
                    poly = [(int(px), int(py)) for px, py in pts]
                    if self._fill is not None:
                        pygame.draw.polygon(self._surf, self._fill, poly)
                    if self._stroke is not None and self._stroke_weight > 0:
                        pygame.draw.polygon(self._surf, self._stroke, poly, int(self._stroke_weight))
        finally:
            self._fill = prev_fill
            self._stroke = prev_stroke
            self._stroke_weight = prev_sw

    def point(self, x: float, y: float, color: Tuple[int, int, int]) -> None:
        if self._is_identity_transform():
            self._surf.set_at((int(x), int(y)), color)
        else:
            tx, ty = self._transform_point(x, y)
            self._surf.set_at((int(tx), int(ty)), color)

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
        try:
            if self._is_identity_transform():
                if w is None or h is None:
                    self._surf.blit(src, (int(x), int(y)))
                else:
                    scaled = pygame.transform.smoothscale(src, (int(w), int(h)))
                    self._surf.blit(scaled, (int(x), int(y)))
            else:
                # Simple image transform support: handle translation + uniform scale + rotation via rotozoom
                # Attempt to detect uniform scale from current matrix; fall back to blit at transformed origin.
                sx, sy = decompose_scale(self._current_matrix())
                avg_scale = (sx + sy) / 2.0 if sx > 0 and sy > 0 else 1.0
                # compute transformed origin
                tx, ty = self._transform_point(x, y)
                try:
                    if w is None or h is None:
                        img_surf = src
                    else:
                        img_surf = pygame.transform.smoothscale(src, (int(w), int(h)))
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
                    self._surf.blit(src, (int(tx), int(ty)))
        except Exception:
            # best-effort: ignore blit errors during examples/tests
            return

    def polygon(self, points: list[tuple[float, float]]) -> None:
        self.polygon_with_style(points)

    def polygon_with_style(self, points: list[tuple[float, float]], fill: Optional[Tuple[int, int, int]] = None, stroke: Optional[Tuple[int, int, int]] = None, stroke_weight: Optional[int] = None, cap: Optional[str] = None, join: Optional[str] = None) -> None:
        if self._is_identity_transform():
            pts = [(int(x), int(y)) for (x, y) in points]
        else:
            ptsf = transform_points(self._current_matrix(), points)
            pts = [(int(px), int(py)) for px, py in ptsf]
        prev_cap = self._line_cap
        prev_join = self._line_join
        try:
            if cap is not None:
                self.set_line_cap(cap)
            if join is not None:
                self.set_line_join(join)

            fill_col = fill if fill is not None else self._fill
            stroke_col = stroke if stroke is not None else self._stroke
            sw = int(stroke_weight) if stroke_weight is not None else int(self._stroke_weight)

            if fill_col is not None:
                pygame.draw.polygon(self._surf, fill_col, pts)
            if stroke_col is not None and sw > 0:
                pygame.draw.polygon(self._surf, stroke_col, pts, sw)
        finally:
            self._line_cap = prev_cap
            self._line_join = prev_join

    # --- shape construction helpers (beginShape/vertex/endShape) ---
    def begin_shape(self) -> None:
        """Start collecting vertices for a custom shape (beginShape in Processing)."""
        self._shape_points = []

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

        if close:
            self.polygon(pts)
        else:
            self.polyline(pts)

        # clear buffer
        self._shape_points = []

    def _flatten_cubic_bezier(self, p0: tuple[float, float], p1: tuple[float, float], p2: tuple[float, float], p3: tuple[float, float], steps: int = 16) -> list[tuple[float, float]]:
        """Sample a cubic Bezier curve and return a list of points including endpoints.

        Uses uniform parameter sampling. For higher-quality tessellation an
        adaptive subdivision could be used but uniform sampling is sufficient
        for many UI and artistic purposes.
        """
        pts: list[tuple[float, float]] = []

        steps = max(2, int(steps))
        for i in range(steps + 1):
            t = i / steps
            # cubic bezier formula
            mt = 1 - t
            x = (mt ** 3) * p0[0] + 3 * (mt ** 2) * t * p1[0] + 3 * mt * (t ** 2) * p2[0] + (t ** 3) * p3[0]
            y = (mt ** 3) * p0[1] + 3 * (mt ** 2) * t * p1[1] + 3 * mt * (t ** 2) * p2[1] + (t ** 3) * p3[1]
            pts.append((x, y))
        return pts

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
        t = float(t)
        mt = 1.0 - t
        # scalar path
        if not hasattr(p0, "__iter__"):
            return (mt ** 3) * p0 + 3 * (mt ** 2) * t * p1 + 3 * mt * (t ** 2) * p2 + (t ** 3) * p3
        # tuple path (assume 2D)
        x = (mt ** 3) * p0[0] + 3 * (mt ** 2) * t * p1[0] + 3 * mt * (t ** 2) * p2[0] + (t ** 3) * p3[0]
        y = (mt ** 3) * p0[1] + 3 * (mt ** 2) * t * p1[1] + 3 * mt * (t ** 2) * p2[1] + (t ** 3) * p3[1]
        return (x, y)

    def bezier_tangent(self, p0, p1, p2, p3, t: float):
        """Compute the derivative (tangent) of the cubic bezier at parameter t.

        Returns a scalar for scalar inputs or a tuple (dx, dy) for 2D inputs.
        """
        t = float(t)
        mt = 1.0 - t
        # derivative of cubic bezier: 3*( (p1-p0)*mt^2 + 2*(p2-p1)*mt*t + (p3-p2)*t^2 )
        if not hasattr(p0, "__iter__"):
            return 3 * ((p1 - p0) * (mt ** 2) + 2 * (p2 - p1) * mt * t + (p3 - p2) * (t ** 2))
        dx = 3 * ((p1[0] - p0[0]) * (mt ** 2) + 2 * (p2[0] - p1[0]) * mt * t + (p3[0] - p2[0]) * (t ** 2))
        dy = 3 * ((p1[1] - p0[1]) * (mt ** 2) + 2 * (p2[1] - p1[1]) * mt * t + (p3[1] - p2[1]) * (t ** 2))
        return (dx, dy)

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
        t = float(t)
        # mt = 1.0 - t
        # tangent scale
        k = (1.0 - float(self._curve_tightness)) * 0.5

        def _eval_scalar(a, b, c, d):
            m1 = k * (c - a)
            m2 = k * (d - b)
            h00 = (2 * t ** 3) - (3 * t ** 2) + 1
            h10 = (t ** 3) - (2 * t ** 2) + t
            h01 = (-2 * t ** 3) + (3 * t ** 2)
            h11 = (t ** 3) - (t ** 2)
            return h00 * b + h10 * m1 + h01 * c + h11 * m2

        # tuple (2D) vs scalar
        if not hasattr(p0, "__iter__"):
            return _eval_scalar(p0, p1, p2, p3)
        x = _eval_scalar(p0[0], p1[0], p2[0], p3[0])
        y = _eval_scalar(p0[1], p1[1], p2[1], p3[1])
        return (x, y)

    def curve_tangent(self, p0, p1, p2, p3, t: float):
        """Compute tangent (derivative) of the curve at parameter t.

        Returns scalar or 2-tuple depending on input.
        """
        t = float(t)
        # tangent scale
        k = (1.0 - float(self._curve_tightness)) * 0.5

        def _eval_scalar_deriv(a, b, c, d):
            m1 = k * (c - a)
            m2 = k * (d - b)
            # derivatives of Hermite basis
            dh00 = 6 * t ** 2 - 6 * t
            dh10 = 3 * t ** 2 - 4 * t + 1
            dh01 = -6 * t ** 2 + 6 * t
            dh11 = 3 * t ** 2 - 2 * t
            return dh00 * b + dh10 * m1 + dh01 * c + dh11 * m2

        if not hasattr(p0, "__iter__"):
            return _eval_scalar_deriv(p0, p1, p2, p3)
        dx = _eval_scalar_deriv(p0[0], p1[0], p2[0], p3[0])
        dy = _eval_scalar_deriv(p0[1], p1[1], p2[1], p3[1])
        return (dx, dy)

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
        # default simple wrapper uses the current stroke/weight
        self.polyline_with_style(points)

    def polyline_with_style(self, points: list[tuple[float, float]], stroke: Optional[Tuple[int, int, int]] = None, stroke_weight: Optional[int] = None, cap: Optional[str] = None, join: Optional[str] = None) -> None:
        """Draw an open polyline connecting the sequence of points with optional per-call styling."""
        if not points:
            return
        prev_cap = self._line_cap
        prev_join = self._line_join
        try:
            if cap is not None:
                self.set_line_cap(cap)
            if join is not None:
                self.set_line_join(join)

            stroke_col = stroke if stroke is not None else self._stroke
            sw = int(stroke_weight) if stroke_weight is not None else int(self._stroke_weight)
            pts = [(int(x), int(y)) for (x, y) in points]
            # pygame.draw.lines draws connected segments; closed=False keeps it open
            if stroke_col is not None and sw > 0:
                pygame.draw.lines(self._surf, stroke_col, False, pts, sw)

                # emulate round caps by drawing circles at endpoints
                if self._line_cap == "round":
                    radius = max(1, int(sw / 2))
                    start = pts[0]
                    end = pts[-1]
                    pygame.draw.circle(self._surf, stroke_col, start, radius)
                    pygame.draw.circle(self._surf, stroke_col, end, radius)

                # emulate round joins by drawing circles at internal vertices
                if self._line_join == "round":
                    radius = max(1, int(sw / 2))
                    for v in pts[1:-1]:
                        pygame.draw.circle(self._surf, stroke_col, v, radius)
        finally:
            self._line_cap = prev_cap
            self._line_join = prev_join

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
    def fill(self, color: Optional[Tuple[int, int, int]]) -> None:
        """Set the fill color. Use `None` to disable filling (noFill())."""
        if color is None:
            self._fill = None
            return
        # Accept Color instances directly
        if isinstance(color, Color):
            self._fill = color.to_tuple()
            return

        # Interpret tuples according to current color mode, using Color helpers
        try:
            mode, m1, _m2, _m3 = self._color_mode
        except Exception:
            mode, m1, _m2, _m3 = ("RGB", 255, 255, 255)

        try:
            if mode == "HSB" and hasattr(color, "__iter__"):
                # allow the Color helper to sanitize/clamp values
                h, s, v = color
                col = Color.from_hsb(h, s, v, max_value=m1)
                self._fill = col.to_tuple()
                return
            # otherwise treat as RGB (values may be in a custom max range)
            if hasattr(color, "__iter__"):
                r, g, b = color
                col = Color.from_rgb(r, g, b, max_value=m1)
                self._fill = col.to_tuple()
                return
        except Exception:
            # best-effort: ignore invalid input
            self._fill = None

    def color_mode(self, mode: Optional[str] = None, max1: int = 255, max2: int = 255, max3: int = 255):
        """Get or set the current color mode.

        - color_mode() -> returns a tuple (mode, max1, max2, max3)
        - color_mode('HSB', 255,255,255) -> sets HSB interpretation for future fill()/stroke() calls
        """
        if mode is None:
            return self._color_mode
        try:
            m = str(mode).upper()
            if m in ("RGB", "HSB"):
                self._color_mode = (m, int(max1), int(max2), int(max3))
        except Exception:
            pass
        return None

    def no_fill(self) -> None:
        """Disable filling for subsequent shape draws."""
        self._fill = None

    def stroke(self, color: Optional[Tuple[int, int, int]]) -> None:
        """Set the stroke color. Use `None` to disable stroke (noStroke())."""
        if color is None:
            self._stroke = None
            return
        if isinstance(color, Color):
            self._stroke = color.to_tuple()
            return

        try:
            mode, m1, _m2, _m3 = self._color_mode
        except Exception:
            mode, m1, _m2, _m3 = ("RGB", 255, 255, 255)

        try:
            if mode == "HSB" and hasattr(color, "__iter__"):
                h, s, v = color
                col = Color.from_hsb(h, s, v, max_value=m1)
                self._stroke = col.to_tuple()
                return
            if hasattr(color, "__iter__"):
                r, g, b = color
                col = Color.from_rgb(r, g, b, max_value=m1)
                self._stroke = col.to_tuple()
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
                    self.fill(fill)
            if stroke is not ...:
                if stroke is None:
                    self.no_stroke()
                else:
                    self.stroke(stroke)
            if stroke_weight is not ...:
                self.stroke_weight(int(stroke_weight))
            if cap is not ...:
                self.set_line_cap(cap)
            if join is not ...:
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

        - Prefers numpy + pygame.surfarray for speed. Falls back to per-pixel reads
          using `Surface.get_at` when numpy/surfarray isn't available.
        - Returns channels=3 (RGB) or 4 (RGBA) depending on surface alpha.
        """
        w, h = self._surf.get_size()
        has_alpha = bool(self._surf.get_flags() & pygame.SRCALPHA)
        # Pure-Python per-pixel copy into nested lists (H x W x C)
        try:
            arr: list[list[tuple[int, ...]]] = []
            for y in range(h):
                row: list[list[int]] = []
                for x in range(w):
                    c = self._surf.get_at((x, y))
                    if has_alpha:
                        # use mutable lists for channel data so callers can assign
                        row.append([c.r, c.g, c.b, c.a])
                    else:
                        row.append([c.r, c.g, c.b])
                arr.append(row)
            return PixelView(arr)
        except Exception:
            return PixelView([])

    def set_pixels(self, arr: Any) -> None:
        """Write a (H,W,3) or (H,W,4) array into the surface.

        Accepts numpy arrays, lists, or other array-like objects. Values are
        clamped/coerced to uint8.
        """
        w, h = self._surf.get_size()
        # unwrap PixelView if provided
        if isinstance(arr, PixelView):
            arr = arr.raw()

        # Expect nested-list shape: arr[h][w] -> tuple
        try:
            for y in range(h):
                row = arr[y]
                for x in range(w):
                    v = row[x]
                    if len(v) == 4:
                        self._surf.set_at((x, y), (int(v[0]) & 255, int(v[1]) & 255, int(v[2]) & 255, int(v[3]) & 255))
                    else:
                        self._surf.set_at((x, y), (int(v[0]) & 255, int(v[1]) & 255, int(v[2]) & 255))
        except Exception as e:
            raise ValueError(f"set_pixels: expected nested list with shape (h,w,c) matching surface {(h,w)}; error: {e}")

    def get_pixel(self, x: int, y: int) -> Tuple[int, ...]:
        """Return a single pixel color tuple (RGB) or (RGBA)."""
        c = self._surf.get_at((int(x), int(y)))
        if bool(self._surf.get_flags() & pygame.SRCALPHA):
            return (c.r, c.g, c.b, c.a)
        return (c.r, c.g, c.b)

    def set_pixel(self, x: int, y: int, color: Tuple[int, ...]) -> None:
        """Set a single pixel color. Accepts (r,g,b) or (r,g,b,a)."""
        self._surf.set_at((int(x), int(y)), color)

    # --- PImage-style pixel helpers ---
    @contextmanager
    def pixels(self):
        """Context manager for pixel access. Yields a `PixelView` and writes
        the data back to the surface on exit.

        Usage:
            with surface.pixels() as pv:
                pv[y,x] = (r,g,b)
        """
        pv = self.get_pixels()
        try:
            yield pv
        finally:
            # Always attempt to write back; let exceptions surface to the caller
            self.set_pixels(pv)

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
            return self

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
        return dest.copy(self, sx, sy, sw, sh, dx, dy, dw, dh)

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
        pts = [(int(x), int(y)) for (x, y) in points]
        if self._fill is not None:
            pygame.draw.polygon(self._surf, self._fill, pts)
        if self._stroke is not None and self._stroke_weight > 0:
            pygame.draw.polygon(self._surf, self._stroke, pts, int(self._stroke_weight))

    # --- shape construction helpers (beginShape/vertex/endShape) ---
    def begin_shape(self) -> None:
        """Start collecting vertices for a custom shape (beginShape in Processing)."""
        self._shape_points = []

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

        if close:
            self.polygon(pts)
        else:
            self.polyline(pts)

        # clear buffer
        self._shape_points = []

    def _flatten_cubic_bezier(self, p0: tuple[float, float], p1: tuple[float, float], p2: tuple[float, float], p3: tuple[float, float], steps: int = 16) -> list[tuple[float, float]]:
        """Sample a cubic Bezier curve and return a list of points including endpoints.

        Uses uniform parameter sampling. For higher-quality tessellation an
        adaptive subdivision could be used but uniform sampling is sufficient
        for many UI and artistic purposes.
        """
        pts: list[tuple[float, float]] = []

        steps = max(2, int(steps))
        for i in range(steps + 1):
            t = i / steps
            # cubic bezier formula
            mt = 1 - t
            x = (mt ** 3) * p0[0] + 3 * (mt ** 2) * t * p1[0] + 3 * mt * (t ** 2) * p2[0] + (t ** 3) * p3[0]
            y = (mt ** 3) * p0[1] + 3 * (mt ** 2) * t * p1[1] + 3 * mt * (t ** 2) * p2[1] + (t ** 3) * p3[1]
            pts.append((x, y))
        return pts

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
        t = float(t)
        mt = 1.0 - t
        # scalar path
        if not hasattr(p0, "__iter__"):
            return (mt ** 3) * p0 + 3 * (mt ** 2) * t * p1 + 3 * mt * (t ** 2) * p2 + (t ** 3) * p3
        # tuple path (assume 2D)
        x = (mt ** 3) * p0[0] + 3 * (mt ** 2) * t * p1[0] + 3 * mt * (t ** 2) * p2[0] + (t ** 3) * p3[0]
        y = (mt ** 3) * p0[1] + 3 * (mt ** 2) * t * p1[1] + 3 * mt * (t ** 2) * p2[1] + (t ** 3) * p3[1]
        return (x, y)

    def bezier_tangent(self, p0, p1, p2, p3, t: float):
        """Compute the derivative (tangent) of the cubic bezier at parameter t.

        Returns a scalar for scalar inputs or a tuple (dx, dy) for 2D inputs.
        """
        t = float(t)
        mt = 1.0 - t
        # derivative of cubic bezier: 3*( (p1-p0)*mt^2 + 2*(p2-p1)*mt*t + (p3-p2)*t^2 )
        if not hasattr(p0, "__iter__"):
            return 3 * ((p1 - p0) * (mt ** 2) + 2 * (p2 - p1) * mt * t + (p3 - p2) * (t ** 2))
        dx = 3 * ((p1[0] - p0[0]) * (mt ** 2) + 2 * (p2[0] - p1[0]) * mt * t + (p3[0] - p2[0]) * (t ** 2))
        dy = 3 * ((p1[1] - p0[1]) * (mt ** 2) + 2 * (p2[1] - p1[1]) * mt * t + (p3[1] - p2[1]) * (t ** 2))
        return (dx, dy)

    def polyline(self, points: list[tuple[float, float]]) -> None:
        """Draw an open polyline connecting the sequence of points.

        Stroke and stroke_weight are respected. Fill is ignored for polylines.
        """
        if not points:
            return
        pts = [(int(x), int(y)) for (x, y) in points]
        # pygame.draw.lines draws connected segments; closed=False keeps it open
        if self._stroke is not None and self._stroke_weight > 0:
            pygame.draw.lines(self._surf, self._stroke, False, pts, int(self._stroke_weight))

            # emulate round caps by drawing circles at endpoints
            if self._line_cap == "round":
                radius = max(1, int(self._stroke_weight / 2))
                start = pts[0]
                end = pts[-1]
                pygame.draw.circle(self._surf, self._stroke, start, radius)
                pygame.draw.circle(self._surf, self._stroke, end, radius)

            # emulate round joins by drawing circles at internal vertices
            if self._line_join == "round":
                radius = max(1, int(self._stroke_weight / 2))
                for v in pts[1:-1]:
                    pygame.draw.circle(self._surf, self._stroke, v, radius)

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

    def arc(self, x: float, y: float, w: float, h: float, start_rad: float, end_rad: float, mode: str = "open", fill: Optional[Tuple[int, int, int]] = None, stroke: Optional[Tuple[int, int, int]] = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None) -> None:
        """Draw an arc. Accepts optional per-call fill/stroke/stroke_weight (or stroke_width).

        This is a best-effort implementation using pygame drawing primitives.
        """
        # Save previous style state
        prev_fill = self._fill
        prev_stroke = self._stroke
        prev_sw = self._stroke_weight
        try:
            if fill is not None:
                self.fill(fill)
            if stroke is not None:
                self.stroke(stroke)
            if stroke_width is not None:
                self.stroke_weight(int(stroke_width))
            elif stroke_weight is not None:
                self.stroke_weight(int(stroke_weight))

            rect = pygame.Rect(int(x - w / 2), int(y - h / 2), int(w), int(h))
            if mode == "open":
                # Draw arc outline only
                if self._stroke is not None:
                    pygame.draw.arc(self._surf, self._stroke, rect, float(start_rad), float(end_rad), int(self._stroke_weight))
            else:
                # For pie/chord, construct polygon points along the ellipse arc
                import math

                steps = max(6, int((end_rad - start_rad) * 10))
                pts = []
                cx = x
                cy = y
                rx = w / 2.0
                ry = h / 2.0
                for i in range(steps + 1):
                    t = start_rad + (end_rad - start_rad) * (i / max(1, steps))
                    px = cx + rx * math.cos(t)
                    py = cy + ry * math.sin(t)
                    pts.append((px, py))
                if mode == "pie":
                    # close to center
                    poly = [(int(cx), int(cy))] + [(int(px), int(py)) for px, py in pts]
                    if self._fill is not None:
                        pygame.draw.polygon(self._surf, self._fill, poly)
                    if self._stroke is not None and self._stroke_weight > 0:
                        pygame.draw.polygon(self._surf, self._stroke, poly, int(self._stroke_weight))
                elif mode == "chord":
                    poly = [(int(px), int(py)) for px, py in pts]
                    if self._fill is not None:
                        pygame.draw.polygon(self._surf, self._fill, poly)
                    if self._stroke is not None and self._stroke_weight > 0:
                        pygame.draw.polygon(self._surf, self._stroke, poly, int(self._stroke_weight))
        finally:
            # Restore previous style state
            self._fill = prev_fill
            self._stroke = prev_stroke
            self._stroke_weight = prev_sw
