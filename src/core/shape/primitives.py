"""Primitive shape helpers: rect, ellipse, circle, line, point, square.

These functions accept an `engine` object as the first argument and record
commands on `engine.graphics`. They forward drawing state (fill/stroke)
from the engine when not explicitly provided.
"""
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def rect(engine: Any, x: float, y: float, w: float, h: float, **kwargs):
    """Record a rectangle draw command on the engine's graphics buffer."""
    try:
        mode = str(getattr(engine, 'rect_mode', 'CORNER')).upper()
    except Exception:
        mode = 'CORNER'

    try:
        if mode == 'CORNER' or mode == 'CORNER':
            x_tl = float(x)
            y_tl = float(y)
            w_w = float(w)
            h_h = float(h)
        elif mode == 'CORNERS':
            x0 = float(x)
            y0 = float(y)
            x1 = float(w)
            y1 = float(h)
            x_tl = min(x0, x1)
            y_tl = min(y0, y1)
            w_w = abs(x1 - x0)
            h_h = abs(y1 - y0)
        elif mode == 'CENTER':
            cx = float(x)
            cy = float(y)
            w_w = float(w)
            h_h = float(h)
            x_tl = cx - (w_w / 2.0)
            y_tl = cy - (h_h / 2.0)
        elif mode == 'RADIUS':
            cx = float(x)
            cy = float(y)
            rx = float(w)
            ry = float(h)
            x_tl = cx - rx
            y_tl = cy - ry
            w_w = rx * 2.0
            h_h = ry * 2.0
        else:
            x_tl = float(x)
            y_tl = float(y)
            w_w = float(w)
            h_h = float(h)
    except Exception:
        x_tl = x
        y_tl = y
        w_w = w
        h_h = h

    if 'fill' not in kwargs:
        kwargs['fill'] = getattr(engine, 'fill_color', None)
    if 'stroke' not in kwargs:
        kwargs['stroke'] = getattr(engine, 'stroke_color', None)
    if 'stroke_weight' not in kwargs:
        kwargs['stroke_weight'] = getattr(engine, 'stroke_weight', 1)
    if 'stroke_cap' not in kwargs:
        kwargs['stroke_cap'] = getattr(engine, 'stroke_cap', None)
    if 'stroke_join' not in kwargs:
        kwargs['stroke_join'] = getattr(engine, 'stroke_join', None)
    return engine.graphics.record('rect', x=x_tl, y=y_tl, w=w_w, h=h_h, **kwargs)


def line(engine: Any, x1: float, y1: float, x2: float, y2: float, **kwargs):
    """Record a line draw command on the engine's graphics buffer."""
    if 'stroke' not in kwargs:
        kwargs['stroke'] = getattr(engine, 'stroke_color', None)
    if 'stroke_weight' not in kwargs:
        kwargs['stroke_weight'] = getattr(engine, 'stroke_weight', 1)
    if 'stroke_cap' not in kwargs:
        kwargs['stroke_cap'] = getattr(engine, 'stroke_cap', None)
    if 'stroke_join' not in kwargs:
        kwargs['stroke_join'] = getattr(engine, 'stroke_join', None)
    return engine.graphics.record('line', x1=x1, y1=y1, x2=x2, y2=y2, **kwargs)


def square(engine: Any, x: float, y: float, size: float, **kwargs):
    """Convenience square -> rect delegate."""
    return rect(engine, x, y, size, size, **kwargs)


def circle(engine: Any, x: float, y: float, r: float, **kwargs):
    """Record a circle draw command on the engine's graphics buffer."""
    if 'fill' not in kwargs:
        kwargs['fill'] = getattr(engine, 'fill_color', None)
    if 'stroke' not in kwargs:
        kwargs['stroke'] = getattr(engine, 'stroke_color', None)
    if 'stroke_weight' not in kwargs:
        kwargs['stroke_weight'] = getattr(engine, 'stroke_weight', 1)
    if 'stroke_cap' not in kwargs:
        kwargs['stroke_cap'] = getattr(engine, 'stroke_cap', None)
    if 'stroke_join' not in kwargs:
        kwargs['stroke_join'] = getattr(engine, 'stroke_join', None)
    return engine.graphics.record('circle', x=x, y=y, r=r, **kwargs)


def ellipse(engine: Any, x: float, y: float, w: float, h: Optional[float] = None, **kwargs):
    """Record an ellipse draw command on the engine's graphics buffer.

    The API mirrors Processing: ellipse(x, y, w, h). If h is None, use w.
    """
    if h is None:
        h = w
    try:
        emode = str(getattr(engine, 'ellipse_mode', 'CENTER')).upper()
    except Exception:
        emode = 'CENTER'

    try:
        if emode == 'CORNER':
            ex = float(x)
            ey = float(y)
            ew = float(w)
            eh = float(h)
        elif emode == 'CORNERS':
            x0 = float(x)
            y0 = float(y)
            x1 = float(w)
            y1 = float(h)
            ex = min(x0, x1)
            ey = min(y0, y1)
            ew = abs(x1 - x0)
            eh = abs(y1 - y0)
        elif emode == 'CENTER':
            cx = float(x)
            cy = float(y)
            ew = float(w)
            eh = float(h)
            ex = cx - (ew / 2.0)
            ey = cy - (eh / 2.0)
        elif emode == 'RADIUS':
            cx = float(x)
            cy = float(y)
            rx = float(w)
            ry = float(h)
            ex = cx - rx
            ey = cy - ry
            ew = rx * 2.0
            eh = ry * 2.0
        else:
            ex = float(x)
            ey = float(y)
            ew = float(w)
            eh = float(h)
    except Exception:
        ex = x
        ey = y
        ew = w
        eh = h
    if 'fill' not in kwargs:
        kwargs['fill'] = getattr(engine, 'fill_color', None)
    if 'stroke' not in kwargs:
        kwargs['stroke'] = getattr(engine, 'stroke_color', None)
    if 'stroke_weight' not in kwargs:
        kwargs['stroke_weight'] = getattr(engine, 'stroke_weight', 1)
    if 'stroke_cap' not in kwargs:
        kwargs['stroke_cap'] = getattr(engine, 'stroke_cap', None)
    if 'stroke_join' not in kwargs:
        kwargs['stroke_join'] = getattr(engine, 'stroke_join', None)
    return engine.graphics.record('ellipse', x=ex, y=ey, w=ew, h=eh, **kwargs)


def stroke_weight(engine: Any, w: int):
    engine.stroke_weight = int(w)


def point(engine: Any, x: float, y: float, **kwargs):
    """Record a point (as a zero-radius circle) to the engine graphics buffer.

    This forwards drawing state similar to `circle` but uses a tiny
    r=0 representation so presenters can treat it efficiently.
    """
    if 'fill' not in kwargs:
        kwargs['fill'] = getattr(engine, 'fill_color', None)
    if 'stroke' not in kwargs:
        kwargs['stroke'] = getattr(engine, 'stroke_color', None)
    if 'stroke_weight' not in kwargs:
        kwargs['stroke_weight'] = getattr(engine, 'stroke_weight', 1)
    if 'stroke_cap' not in kwargs:
        kwargs['stroke_cap'] = getattr(engine, 'stroke_cap', None)
    if 'stroke_join' not in kwargs:
        kwargs['stroke_join'] = getattr(engine, 'stroke_join', None)
    return engine.graphics.record('point', x=x, y=y, **kwargs)


def _triangle_fan(engine: Any, cx: float, cy: float, radius: float, segments: int = 36, start_angle: float = 0.0):
    """Internal helper: record a TRIANGLE_FAN around a center using `segments` slices.

    Kept internal (prefixed with underscore) so it does not expand the public
    sketch API.
    """
    try:
        import math

        step = 360.0 / float(max(1, int(segments)))
        for i in range(int(segments)):
            a1 = (start_angle + i * step) * math.pi / 180.0
            a2 = (start_angle + (i + 1) * step) * math.pi / 180.0
            x1 = float(cx) + float(radius) * math.cos(a1)
            y1 = float(cy) + float(radius) * math.sin(a1)
            x2 = float(cx) + float(radius) * math.cos(a2)
            y2 = float(cy) + float(radius) * math.sin(a2)
            engine.graphics.record('shape', mode='TRIANGLES', vertices=[(float(cx), float(cy)), (x1, y1), (x2, y2)], close=False)
    except Exception:
        pass
