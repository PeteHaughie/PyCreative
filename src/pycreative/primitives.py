from __future__ import annotations

from typing import Optional, Tuple, Sequence, cast

import pygame

from .color import Color
from .utils import has_alpha, draw_alpha_polygon_on_temp, draw_alpha_rect_on_temp


def _ensure_color_tuple(surface, c: object) -> Optional[Tuple[int, ...]]:
    """Return a concrete tuple of ints for a color-like value or None.

    This normalizes pycreative Color instances, numeric tuples/lists, or other
    color-like inputs into a (r,g,b) or (r,g,b,a) tuple of ints suitable for
    passing to pygame.draw.* APIs. If normalization fails, returns None.
    """
    if c is None:
        return None
    try:
        # If it's our Color class, delegate to Surface coercion which already
        # understands color modes and ranges.
        if isinstance(c, Color):
            return cast(Optional[Tuple[int, ...]], surface._coerce_input_color(c))
        # If it's already a tuple/list of numbers, coerce entries to ints.
        if isinstance(c, (tuple, list)):
            vals = tuple(int(v) & 255 for v in c)
            if len(vals) in (3, 4):
                return vals
            return None
        # Fallback: try the surface coercion (it handles numeric grayscale)
        return cast(Optional[Tuple[int, ...]], surface._coerce_input_color(c))
    except Exception:
        return None


def rect(surface, x: float, y: float, w: float, h: float, fill: Optional[Tuple[int, ...]] = None, stroke: Optional[Tuple[int, ...]] = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None, cap: Optional[str] = None, join: Optional[str] = None) -> None:
    # compute topleft depending on mode
    if surface._rect_mode == surface.MODE_CENTER:
        tlx = x - w / 2
        tly = y - h / 2
    else:
        tlx = x
        tly = y

    # initialize locals so static analysis can reason about them
    rect: Optional[pygame.Rect] = None
    pts: list[tuple[float, float]] = []

    # If no transform is active use the fast path with integers
    if surface._is_identity_transform():
        left = float(tlx)
        top = float(tly)
        width = float(w)
        height = float(h)
        if width < 0:
            left = left + width
            width = -width
        if height < 0:
            top = top + height
            height = -height
        rect = pygame.Rect(int(left), int(top), int(width), int(height))
        draw_polygon = False
    else:
        pts = [
            (tlx, tly),
            (tlx + w, tly),
            (tlx + w, tly + h),
            (tlx, tly + h),
        ]
        pts = surface.transform_points(pts) if hasattr(surface, 'transform_points') else surface._current_matrix()
        pts = surface._current_matrix() and pts or pts
        # fallback: draw polygon
        draw_polygon = True
    # ensure pts and rect are defined for type-checkers (already initialized above)

    prev_cap = surface._line_cap
    prev_join = surface._line_join
    try:
        if cap is not None:
            surface.set_line_cap(cap)
        if join is not None:
            surface.set_line_join(join)

        if stroke_width is not None:
            sw = int(stroke_width)
        elif stroke_weight is not None:
            sw = int(stroke_weight)
        else:
            sw = int(surface._stroke_weight)

        fill_col = fill if fill is not None else surface._fill
        stroke_col = stroke if stroke is not None else surface._stroke

        # Try to coerce Color instances or other high-level color objects
        try:
            if fill is not None or isinstance(fill_col, Color):
                fill_col = surface._coerce_input_color(fill_col)
        except Exception:
            pass
        try:
            if stroke is not None or isinstance(stroke_col, Color):
                stroke_col = surface._coerce_input_color(stroke_col)
        except Exception:
            pass

        # Normalize color-like inputs to concrete tuples for pygame APIs
        fill_col = _ensure_color_tuple(surface, fill_col)
        stroke_col = _ensure_color_tuple(surface, stroke_col)

        # Fill
        if fill_col is not None:
            if fill_col is not None and has_alpha(fill_col):
                if draw_polygon:
                    xs = [int(px) for px, _ in pts]
                    ys = [int(py) for _, py in pts]
                    minx, maxx = min(xs), max(xs)
                    miny, maxy = min(ys), max(ys)
                    rw = max(1, maxx - minx)
                    rh = max(1, maxy - miny)
                    temp = surface._get_temp_surface(rw, rh)
                    rel_pts = [(px - minx, py - miny) for px, py in pts]
                    draw_alpha_polygon_on_temp(surface._surf, temp, rel_pts, cast(Tuple[int, ...], fill_col), minx, miny)
                else:
                    if rect is not None:
                        temp = surface._get_temp_surface(rect.width, rect.height)
                        draw_alpha_rect_on_temp(surface._surf, temp, rect, cast(Tuple[int, ...], fill_col))
            else:
                if draw_polygon:
                    pygame.draw.polygon(surface._surf, cast(Tuple[int, ...], fill_col), [(int(px), int(py)) for px, py in pts])
                else:
                    if rect is not None:
                        pygame.draw.rect(surface._surf, cast(Tuple[int, ...], fill_col), rect)

        # Stroke
        if stroke_col is not None and sw > 0:
            if stroke_col is not None and has_alpha(stroke_col):
                if draw_polygon:
                    xs = [int(px) for px, _ in pts]
                    ys = [int(py) for _, py in pts]
                    minx, maxx = min(xs), max(xs)
                    miny, maxy = min(ys), max(ys)
                    rw = max(1, maxx - minx)
                    rh = max(1, maxy - miny)
                    temp = surface._get_temp_surface(rw, rh)
                    rel_pts = [(px - minx, py - miny) for px, py in pts]
                    pygame.draw.polygon(temp, cast(Tuple[int, ...], stroke_col), [(int(px), int(py)) for px, py in rel_pts], sw)
                    surface._surf.blit(temp, (minx, miny))
                else:
                    if rect is not None:
                        temp = surface._get_temp_surface(rect.width, rect.height)
                        pygame.draw.rect(temp, cast(Tuple[int, ...], stroke_col), pygame.Rect(0, 0, rect.width, rect.height), sw)
                        surface._surf.blit(temp, (rect.left, rect.top))
            else:
                if draw_polygon:
                    pygame.draw.polygon(surface._surf, cast(Tuple[int, ...], stroke_col), [(int(px), int(py)) for px, py in pts], sw)
                else:
                    if rect is not None:
                        pygame.draw.rect(surface._surf, cast(Tuple[int, ...], stroke_col), rect, sw)
    finally:
        surface._line_cap = prev_cap
        surface._line_join = prev_join


def square(
    surface,
    x: float,
    y: float,
    s: float,
    fill: Optional[Tuple[int, ...]] = None,
    stroke: Optional[Tuple[int, ...]] = None,
    stroke_weight: Optional[int] = None,
    stroke_width: Optional[int] = None,
    cap: Optional[str] = None,
    join: Optional[str] = None,
) -> None:
    """Draw a square with side length `s`.

    This is a thin wrapper that forwards to `rect()` using `w = h = s` so
    behavior (modes, transforms, alpha handling) is shared with rectangles.
    """
    return rect(
        surface,
        x,
        y,
        s,
        s,
        fill=fill,
        stroke=stroke,
        stroke_weight=stroke_weight,
        stroke_width=stroke_width,
        cap=cap,
        join=join,
    )


def ellipse(surface, x: float, y: float, w: float, h: float, fill: Optional[Tuple[int, ...]] = None, stroke: Optional[Tuple[int, ...]] = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None, cap: Optional[str] = None, join: Optional[str] = None) -> None:
    if surface._ellipse_mode == surface.MODE_CENTER:
        cx = x
        cy = y
        rx = w / 2.0
        ry = h / 2.0
    else:
        cx = x + w / 2.0
        cy = y + h / 2.0
        rx = w / 2.0
        ry = h / 2.0

    prev_cap = surface._line_cap
    prev_join = surface._line_join
    try:
        if cap is not None:
            surface.set_line_cap(cap)
        if join is not None:
            surface.set_line_join(join)

        if stroke_width is not None:
            sw = int(stroke_width)
        elif stroke_weight is not None:
            sw = int(stroke_weight)
        else:
            sw = int(surface._stroke_weight)

        fill_col = fill if fill is not None else surface._fill
        stroke_col = stroke if stroke is not None else surface._stroke

        # Normalize colors
        fill_col = _ensure_color_tuple(surface, fill_col)
        stroke_col = _ensure_color_tuple(surface, stroke_col)

        if surface._is_identity_transform():
            if surface._ellipse_mode == surface.MODE_CENTER:
                rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
            else:
                rect = pygame.Rect(int(x), int(y), int(w), int(h))

            def _has_alpha(c):
                return isinstance(c, tuple) and len(c) == 4 and c[3] != 255

            if isinstance(fill_col, tuple) and len(fill_col) == 4 and fill_col[3] != 255:
                temp = surface._get_temp_surface(rect.width, rect.height)
                pygame.draw.ellipse(temp, cast(Tuple[int, ...], fill_col), pygame.Rect(0, 0, rect.width, rect.height))
                surface._surf.blit(temp, (rect.left, rect.top))
            else:
                if fill_col is not None:
                    pygame.draw.ellipse(surface._surf, fill_col, rect)

            if isinstance(stroke_col, tuple) and len(stroke_col) == 4 and stroke_col[3] != 255 and sw > 0:
                temp = surface._get_temp_surface(rect.width, rect.height)
                pygame.draw.ellipse(temp, cast(Tuple[int, ...], stroke_col), pygame.Rect(0, 0, rect.width, rect.height), sw)
                surface._surf.blit(temp, (rect.left, rect.top))
            else:
                if stroke_col is not None and sw > 0:
                    pygame.draw.ellipse(surface._surf, stroke_col, rect, sw)
        else:
            import math

            samples = max(24, int(2 * math.pi * max(rx, ry) / 6))
            pts = []
            for i in range(samples):
                t = (i / samples) * 2 * math.pi
                px = cx + rx * math.cos(t)
                py = cy + ry * math.sin(t)
                pts.append((px, py))
            pts = surface.transform_points(pts) if hasattr(surface, 'transform_points') else pts
            int_pts = [(int(px), int(py)) for px, py in pts]
            if fill_col is not None:
                pygame.draw.polygon(surface._surf, fill_col, int_pts)
            if stroke_col is not None and sw > 0:
                pygame.draw.polygon(surface._surf, stroke_col, int_pts, sw)
    finally:
        surface._line_cap = prev_cap
        surface._line_join = prev_join


def circle(surface, x: float, y: float, d: float, fill: Optional[Tuple[int, ...]] = None, stroke: Optional[Tuple[int, ...]] = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None, cap: Optional[str] = None, join: Optional[str] = None) -> None:
    ellipse(surface, x, y, d, d, fill=fill, stroke=stroke, stroke_weight=stroke_weight, stroke_width=stroke_width, cap=cap, join=join)


def line(surface, x1: float, y1: float, x2: float, y2: float, color: Optional[Tuple[int, ...]] = None, width: Optional[int] = None, stroke: Optional[Tuple[int, ...]] = None, stroke_width: Optional[int] = None, cap: Optional[str] = None, join: Optional[str] = None) -> None:
    col = stroke if stroke is not None else (color if color is not None else surface._stroke)
    if stroke_width is not None:
        w = int(stroke_width)
    else:
        w = int(width) if width is not None else int(surface._stroke_weight)
    if col is None or w <= 0:
        return

    prev_cap = surface._line_cap
    prev_join = surface._line_join
    try:
        if cap is not None:
            surface.set_line_cap(cap)
        if join is not None:
            surface.set_line_join(join)

        try:
            if isinstance(col, Color):
                col = surface._coerce_input_color(col)
            elif isinstance(col, (list, tuple)) and len(col) in (3, 4):
                col = tuple(int(v) & 255 for v in col)
        except Exception:
            pass

        # Ensure concrete tuple for pygame
        col = _ensure_color_tuple(surface, col)

        def _has_alpha(c):
            return isinstance(c, tuple) and len(c) == 4 and c[3] != 255

        if surface._is_identity_transform():
            if _has_alpha(col):
                minx = min(int(x1), int(x2))
                miny = min(int(y1), int(y2))
                maxx = max(int(x1), int(x2))
                maxy = max(int(y1), int(y2))
                w_box = max(1, maxx - minx + int(w) * 2)
                h_box = max(1, maxy - miny + int(w) * 2)
                temp = surface._get_temp_surface(w_box, h_box)
                rel_p1 = (int(x1) - minx + int(w), int(y1) - miny + int(w))
                rel_p2 = (int(x2) - minx + int(w), int(y2) - miny + int(w))
                pygame.draw.line(temp, cast(Tuple[int, ...], col), rel_p1, rel_p2, int(w))
                surface._surf.blit(temp, (minx - int(w), miny - int(w)))
            else:
                pygame.draw.line(surface._surf, cast(Tuple[int, ...], col), (int(x1), int(y1)), (int(x2), int(y2)), int(w))
        else:
            p1 = surface._transform_point(x1, y1)
            p2 = surface._transform_point(x2, y2)
            pygame.draw.line(surface._surf, cast(Tuple[int, ...], col), (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), int(w))

        if surface._line_cap == "round":
            radius = max(1, int(w / 2))
            pygame.draw.circle(surface._surf, cast(Tuple[int, ...], col), (int(x1), int(y1)), radius)
            pygame.draw.circle(surface._surf, cast(Tuple[int, ...], col), (int(x2), int(y2)), radius)
    finally:
        surface._line_cap = prev_cap
        surface._line_join = prev_join


def triangle(surface, x1, y1, x2, y2, x3, y3, fill: Optional[Tuple[int, ...]] = None, stroke: Optional[Tuple[int, ...]] = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None) -> None:
    pts = [(x1, y1), (x2, y2), (x3, y3)]
    sw = int(stroke_width) if stroke_width is not None else (int(stroke_weight) if stroke_weight is not None else None)
    polygon_with_style(surface, pts, fill=fill, stroke=stroke, stroke_weight=sw)


def quad(surface, x1, y1, x2, y2, x3, y3, x4, y4, fill: Optional[Tuple[int, ...]] = None, stroke: Optional[Tuple[int, ...]] = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None) -> None:
    pts = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    sw = int(stroke_width) if stroke_width is not None else (int(stroke_weight) if stroke_weight is not None else None)
    polygon_with_style(surface, pts, fill=fill, stroke=stroke, stroke_weight=sw)


def arc(surface, x: float, y: float, w: float, h: float, start_rad: float, end_rad: float, mode: str = "open", fill: Optional[Tuple[int, ...]] = None, stroke: Optional[Tuple[int, ...]] = None, stroke_weight: Optional[int] = None, stroke_width: Optional[int] = None) -> None:
    prev_fill = surface._fill
    prev_stroke = surface._stroke
    prev_sw = surface._stroke_weight
    try:
        if fill is not None:
            if fill is None:
                surface._fill = None
            elif isinstance(fill, Color):
                try:
                    surface._fill = fill.to_rgba_tuple()
                except Exception:
                    surface._fill = fill.to_tuple()
            else:
                try:
                    modec = surface._color_mode[0]
                    m1 = int(surface._color_mode[1])
                    _m2 = int(surface._color_mode[2])
                    _m3 = int(surface._color_mode[3])
                except Exception:
                    modec, m1, _m2, _m3 = ("RGB", 255, 255, 255)
                try:
                    if modec == "HSB" and hasattr(fill, "__iter__"):
                        vals = list(fill)
                        h, s, v = vals[0], vals[1], vals[2]
                        ma = int(surface._color_mode[4]) if len(surface._color_mode) >= 5 else m1
                        col = Color.from_hsb(h, s, v, max_h=m1, max_s=_m2, max_v=_m3, max_a=ma)
                        if len(vals) >= 4:
                            a = int(vals[3]) & 255
                            surface._fill = (col.r, col.g, col.b, a)
                        else:
                            surface._fill = col.to_tuple()
                    elif hasattr(fill, "__iter__"):
                        vals = list(fill)
                        r, g, b = vals[0], vals[1], vals[2]
                        col = Color.from_rgb(r, g, b, max_value=m1)
                        if len(vals) >= 4:
                            a = int(vals[3]) & 255
                            surface._fill = (col.r, col.g, col.b, a)
                        else:
                            surface._fill = col.to_tuple()
                    else:
                        surface._fill = None
                except Exception:
                    surface._fill = None
        if stroke is not None:
            surface.stroke(stroke)
        if stroke_width is not None:
            surface.stroke_weight(int(stroke_width))
        elif stroke_weight is not None:
            surface.stroke_weight(int(stroke_weight))
        rect = pygame.Rect(int(x - w / 2), int(y - h / 2), int(w), int(h))
        if mode == "open":
            if surface._stroke is not None:
                pygame.draw.arc(surface._surf, surface._stroke, rect, float(start_rad), float(end_rad), int(surface._stroke_weight))
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
                polygon_with_style(surface, poly, fill=surface._fill, stroke=surface._stroke, stroke_weight=surface._stroke_weight)
            elif mode == "chord":
                poly = [(int(px), int(py)) for px, py in pts]
                polygon_with_style(surface, poly, fill=surface._fill, stroke=surface._stroke, stroke_weight=surface._stroke_weight)
    finally:
        surface._fill = prev_fill
        surface._stroke = prev_stroke
        surface._stroke_weight = prev_sw


def point(surface, x: float, y: float, color: Optional[Tuple[int, ...]] = None, z: Optional[float] = None) -> None:
    draw_color = color if color is not None else surface._stroke
    draw_color = _ensure_color_tuple(surface, draw_color)
    if draw_color is None:
        return
    if surface._is_identity_transform():
        tx = float(x)
        ty = float(y)
    else:
        tx, ty = surface._transform_point(x, y)
    ix = int(round(tx))
    iy = int(round(ty))
    sw = max(1, int(surface._stroke_weight))
    try:
        if sw <= 1:
            surface._surf.set_at((ix, iy), draw_color)
        else:
            size = sw
            tmp = surface._get_temp_surface(size, size)
            cx = size // 2
            cy = size // 2
            pygame.draw.circle(tmp, draw_color, (cx, cy), size // 2)
            surface._surf.blit(tmp, (ix - cx, iy - cy))
    except Exception:
        return


def polygon_with_style(surface, points: Sequence[tuple[float, float]], fill: Optional[Tuple[int, ...]] = None, stroke: Optional[Tuple[int, ...]] = None, stroke_weight: Optional[int] = None, cap: Optional[str] = None, join: Optional[str] = None) -> None:
    if surface._is_identity_transform():
        pts = [(int(round(x)), int(round(y))) for (x, y) in points]
    else:
        # When a transform is active, apply it to the vertex list so
        # polygons/triangles respect translate/rotate/scale on the surface.
        ptsf = points
        try:
            # Use the public helper which understands the surface matrix.
            ptsf = surface.transform_points(points)
        except Exception:
            ptsf = points
        pts = [(int(round(px)), int(round(py))) for px, py in ptsf]
    prev_cap = surface._line_cap
    prev_join = surface._line_join
    try:
        if cap is not None:
            surface.set_line_cap(cap)
        if join is not None:
            surface.set_line_join(join)

        fill_col = fill if fill is not None else surface._fill
        stroke_col = stroke if stroke is not None else surface._stroke
        try:
            if fill is not None or isinstance(fill_col, Color):
                fill_col = surface._coerce_input_color(fill_col)
        except Exception:
            pass
        try:
            if stroke is not None or isinstance(stroke_col, Color):
                stroke_col = surface._coerce_input_color(stroke_col)
        except Exception:
            pass
        # Normalize colors for pygame calls
        fill_col = _ensure_color_tuple(surface, fill_col)
        stroke_col = _ensure_color_tuple(surface, stroke_col)
        sw = int(stroke_weight) if stroke_weight is not None else int(surface._stroke_weight)

        def _has_alpha(c):
            return isinstance(c, tuple) and len(c) == 4 and c[3] != 255

        if _has_alpha(fill_col):
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            minx, maxx = min(xs), max(xs)
            miny, maxy = min(ys), max(ys)
            w = max(1, maxx - minx)
            h = max(1, maxy - miny)
            temp = surface._get_temp_surface(w, h)
            rel_pts = [((px - minx), (py - miny)) for px, py in pts]
            pygame.draw.polygon(temp, cast(Tuple[int, ...], fill_col), [(int(round(px)), int(round(py))) for px, py in rel_pts])
            surface._surf.blit(temp, (minx, miny))
        else:
            if fill_col is not None:
                pygame.draw.polygon(surface._surf, cast(Tuple[int, ...], fill_col), pts)

        if _has_alpha(stroke_col) and sw > 0:
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            minx0, maxx0 = min(xs), max(xs)
            miny0, maxy0 = min(ys), max(ys)
            pad = max(2, int(sw) + 2)
            w = max(1, int(maxx0 - minx0) + pad * 2)
            h = max(1, int(maxy0 - miny0) + pad * 2)
            temp = surface._get_temp_surface(w, h)
            rel_pts = [((px - minx0) + pad, (py - miny0) + pad) for px, py in pts]
            n = len(rel_pts)
            int_rel = [(int(round(p[0])), int(round(p[1]))) for p in rel_pts]
            for i in range(n):
                a = int_rel[i]
                b = int_rel[(i + 1) % n]
                pygame.draw.line(temp, cast(Tuple[int, ...], stroke_col), a, b, sw)
            radius = max(1, int(sw / 2))
            for v in int_rel:
                pygame.draw.circle(temp, cast(Tuple[int, ...], stroke_col), v, radius)
            surface._surf.blit(temp, (int(minx0 - pad), int(miny0 - pad)))
        else:
            if stroke_col is not None and sw > 0:
                n = len(pts)
                for i in range(n):
                    a = pts[i]
                    b = pts[(i + 1) % n]
                    pygame.draw.line(surface._surf, cast(Tuple[int, ...], stroke_col), a, b, sw)
                radius = max(1, int(sw / 2))
                for v in pts:
                    pygame.draw.circle(surface._surf, cast(Tuple[int, ...], stroke_col), (int(round(v[0])), int(round(v[1]))), radius)
    finally:
        surface._line_cap = prev_cap
        surface._line_join = prev_join


def polygon(surface, points: list[tuple[float, float]]) -> None:
    polygon_with_style(surface, points)


def polyline(surface, points: list[tuple[float, float]]) -> None:
    if surface._is_identity_transform():
        pts = [(int(round(x)), int(round(y))) for (x, y) in points]
    else:
        ptsf = points
        try:
            ptsf = surface.transform_points(points)
        except Exception:
            ptsf = points
        pts = [(int(round(px)), int(round(py))) for px, py in ptsf]
    # draw lines between successive points
    if pts:
        n = len(pts)
        stroke_col = surface._stroke if surface._stroke is not None else surface._fill
        sw = int(surface._stroke_weight)
        if stroke_col is None or sw <= 0:
            return

        stroke_col = _ensure_color_tuple(surface, stroke_col)

        # If stroke has alpha, draw onto a temporary SRCALPHA surface and blit
        if has_alpha(stroke_col):
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            minx, maxx = min(xs), max(xs)
            miny, maxy = min(ys), max(ys)
            pad = max(1, int(sw))
            w = max(1, maxx - minx + pad * 2)
            h = max(1, maxy - miny + pad * 2)
            temp = surface._get_temp_surface(w, h)
            rel_pts = [((px - minx) + pad, (py - miny) + pad) for px, py in pts]
            int_rel = [(int(round(p[0])), int(round(p[1]))) for p in rel_pts]
            # draw lines and round end-caps
            for i in range(len(int_rel) - 1):
                a = int_rel[i]
                b = int_rel[i + 1]
                pygame.draw.line(temp, cast(Tuple[int, ...], stroke_col), a, b, sw)
            radius = max(1, int(sw / 2))
            for v in int_rel:
                pygame.draw.circle(temp, cast(Tuple[int, ...], stroke_col), v, radius)
            surface._surf.blit(temp, (int(minx - pad), int(miny - pad)))
        else:
            for i in range(n - 1):
                a = pts[i]
                b = pts[i + 1]
                pygame.draw.line(surface._surf, cast(Tuple[int, ...], stroke_col), a, b, sw)
