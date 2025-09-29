from __future__ import annotations

from typing import Optional, Tuple

import pygame


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
        self._shape_points = []

    @property
    def size(self) -> Tuple[int, int]:
        return self._surf.get_size()

    @property
    def raw(self) -> pygame.Surface:
        return self._surf

    # --- state setters (Processing-like names simplified for Python) ---
    def fill(self, color: Optional[Tuple[int, int, int]]):
        """Set fill color; pass None to disable fill."""
        self._fill = color

    def no_fill(self) -> None:
        self._fill = None

    def stroke(self, color: Optional[Tuple[int, int, int]]):
        """Set stroke color; pass None to disable stroke."""
        self._stroke = color

    def no_stroke(self) -> None:
        self._stroke = None

    def stroke_weight(self, w: int) -> None:
        self._stroke_weight = max(1, int(w))

    def rect_mode(self, mode: str) -> None:
        if mode in (self.MODE_CORNER, self.MODE_CENTER):
            self._rect_mode = mode

    def ellipse_mode(self, mode: str) -> None:
        if mode in (self.MODE_CORNER, self.MODE_CENTER):
            self._ellipse_mode = mode

    # --- basic operations ---
    def clear(self, color: Tuple[int, int, int]) -> None:
        self._surf.fill(color)

    def rect(self, x: float, y: float, w: float, h: float) -> None:
        # compute topleft depending on mode
        if self._rect_mode == self.MODE_CENTER:
            tlx = int(x - w / 2)
            tly = int(y - h / 2)
        else:
            tlx = int(x)
            tly = int(y)
        rect = pygame.Rect(tlx, tly, int(w), int(h))
        # fill then stroke
        if self._fill is not None:
            pygame.draw.rect(self._surf, self._fill, rect)
        if self._stroke is not None and self._stroke_weight > 0:
            pygame.draw.rect(self._surf, self._stroke, rect, int(self._stroke_weight))

    def ellipse(self, x: float, y: float, w: float, h: float) -> None:
        # ellipse mode: center or corner
        if self._ellipse_mode == self.MODE_CENTER:
            rect = pygame.Rect(int(x - w / 2), int(y - h / 2), int(w), int(h))
        else:
            rect = pygame.Rect(int(x), int(y), int(w), int(h))
        if self._fill is not None:
            pygame.draw.ellipse(self._surf, self._fill, rect)
        if self._stroke is not None and self._stroke_weight > 0:
            pygame.draw.ellipse(self._surf, self._stroke, rect, int(self._stroke_weight))

    def line(self, x1: float, y1: float, x2: float, y2: float, color: Tuple[int, int, int], width: int = 1) -> None:
        pygame.draw.line(self._surf, color, (int(x1), int(y1)), (int(x2), int(y2)), int(width))

    def point(self, x: float, y: float, color: Tuple[int, int, int]) -> None:
        self._surf.set_at((int(x), int(y)), color)

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
            if w is None or h is None:
                self._surf.blit(src, (int(x), int(y)))
            else:
                scaled = pygame.transform.smoothscale(src, (int(w), int(h)))
                self._surf.blit(scaled, (int(x), int(y)))
        except Exception:
            # best-effort: ignore blit errors during examples/tests
            return


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
        """Add a vertex to the current shape under construction."""
        self._shape_points.append((x, y))

    def end_shape(self, close: bool = False) -> None:
        """Finish the current shape and draw it.

        If `close` is True the shape is closed (polygon), otherwise it's drawn
        as an open polyline.
        """
        if not self._shape_points:
            return
        if close:
            self.polygon(self._shape_points)
        else:
            self.polyline(self._shape_points)
        # clear buffer
        self._shape_points = []

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

    def arc(self, x: float, y: float, w: float, h: float, start_rad: float, end_rad: float, mode: str = "open") -> None:
        """Draw an arc. mode can be 'open' (stroke-only arc), 'pie' (filled pie), or 'chord'.

        This is a best-effort implementation using pygame drawing primitives.
        """
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
