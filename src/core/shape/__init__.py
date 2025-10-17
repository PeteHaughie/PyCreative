"""Shape helpers: small, engine-aware functions for recording shape ops.

These functions accept an `engine` as the first argument to remain
implementation-focused and avoid import-time cycles with the Engine.
"""
from typing import Any
from typing import Optional


def rect(engine: Any, x: float, y: float, w: float, h: float, **kwargs):
    """Record a rectangle draw command on the engine's graphics buffer."""
    # Interpret rect parameters according to engine.rect_mode if present.
    # Supported modes (Processing-style): CORNER (default), CORNERS, CENTER, RADIUS
    try:
        mode = str(getattr(engine, 'rect_mode', 'CORNER')).upper()
    except Exception:
        mode = 'CORNER'

    # Normalize arguments to canonical (x_top_left, y_top_left, width, height)
    try:
        if mode == 'CORNER' or mode == 'CORNER':
            x_tl = float(x)
            y_tl = float(y)
            w_w = float(w)
            h_h = float(h)
        elif mode == 'CORNERS':
            # x,y,x2,y2 passed as x,y,w,h; treat w,h as x2,y2
            x0 = float(x)
            y0 = float(y)
            x1 = float(w)
            y1 = float(h)
            x_tl = min(x0, x1)
            y_tl = min(y0, y1)
            w_w = abs(x1 - x0)
            h_h = abs(y1 - y0)
        elif mode == 'CENTER':
            # x,y is center; w,h are full width/height
            cx = float(x)
            cy = float(y)
            w_w = float(w)
            h_h = float(h)
            x_tl = cx - (w_w / 2.0)
            y_tl = cy - (h_h / 2.0)
        elif mode == 'RADIUS':
            # x,y is center; w,h are radii
            cx = float(x)
            cy = float(y)
            rx = float(w)
            ry = float(h)
            x_tl = cx - rx
            y_tl = cy - ry
            w_w = rx * 2.0
            h_h = ry * 2.0
        else:
            # unknown mode: fallback to CORNER behaviour
            x_tl = float(x)
            y_tl = float(y)
            w_w = float(w)
            h_h = float(h)
    except Exception:
        # If conversion fails, use raw values
        x_tl = x
        y_tl = y
        w_w = w
        h_h = h

    # forward drawing state if not specified
    if 'fill' not in kwargs:
        kwargs['fill'] = getattr(engine, 'fill_color', None)
    if 'stroke' not in kwargs:
        kwargs['stroke'] = getattr(engine, 'stroke_color', None)
    if 'stroke_weight' not in kwargs:
        kwargs['stroke_weight'] = getattr(engine, 'stroke_weight', 1)
    return engine.graphics.record('rect', x=x_tl, y=y_tl, w=w_w, h=h_h, **kwargs)


def line(engine: Any, x1: float, y1: float, x2: float, y2: float, **kwargs):
    """Record a line draw command on the engine's graphics buffer."""
    if 'stroke' not in kwargs:
        kwargs['stroke'] = getattr(engine, 'stroke_color', None)
    if 'stroke_weight' not in kwargs:
        kwargs['stroke_weight'] = getattr(engine, 'stroke_weight', 1)
    return engine.graphics.record('line', x1=x1, y1=y1, x2=x2, y2=y2, **kwargs)


def square(engine: Any, x: float, y: float, size: float, **kwargs):
    """Convenience square -> rect delegate."""
    return rect(engine, x, y, size, size, **kwargs)


def circle(engine: Any, x: float, y: float, r: float, **kwargs):
    """Record a circle draw command on the engine's graphics buffer."""
    # forward drawing state if not specified
    if 'fill' not in kwargs:
        kwargs['fill'] = getattr(engine, 'fill_color', None)
    if 'stroke' not in kwargs:
        kwargs['stroke'] = getattr(engine, 'stroke_color', None)
    if 'stroke_weight' not in kwargs:
        kwargs['stroke_weight'] = getattr(engine, 'stroke_weight', 1)
    return engine.graphics.record('circle', x=x, y=y, r=r, **kwargs)


def ellipse(engine: Any, x: float, y: float, w: float, h: Optional[float] = None, **kwargs):
    """Record an ellipse draw command on the engine's graphics buffer.

    The API mirrors Processing: ellipse(x, y, w, h). If h is None, use w.
    """
    if h is None:
        h = w
    # Interpret ellipse parameters according to engine.ellipse_mode if present.
    # Supported modes (Processing-style): CORNER (default), CORNERS, CENTER, RADIUS
    try:
        emode = str(getattr(engine, 'ellipse_mode', 'CENTER')).upper()
    except Exception:
        emode = 'CENTER'

    # Normalize to canonical (x_top_left, y_top_left, width, height) where
    # ellipse recording expects center-like params converted to top-left + w/h
    try:
        if emode == 'CORNER':
            ex = float(x)
            ey = float(y)
            ew = float(w)
            eh = float(h)
        elif emode == 'CORNERS':
            # x,y,x2,y2 passed as x,y,w,h; treat w,h as x2,y2
            x0 = float(x)
            y0 = float(y)
            x1 = float(w)
            y1 = float(h)
            ex = min(x0, x1)
            ey = min(y0, y1)
            ew = abs(x1 - x0)
            eh = abs(y1 - y0)
        elif emode == 'CENTER':
            # x,y is center; w,h are full width/height
            cx = float(x)
            cy = float(y)
            ew = float(w)
            eh = float(h)
            ex = cx - (ew / 2.0)
            ey = cy - (eh / 2.0)
        elif emode == 'RADIUS':
            # x,y is center; w,h are radii
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
    return engine.graphics.record('ellipse', x=ex, y=ey, w=ew, h=eh, **kwargs)


def stroke_weight(engine: Any, w: int):
    engine.stroke_weight = int(w)


def point(engine: Any, x: float, y: float, **kwargs):
    """Record a point (as a zero-radius circle) to the engine graphics buffer.

    This forwards drawing state similar to `circle` but uses a tiny
    r=0 representation so presenters can treat it efficiently.
    """
    # forward drawing state if not specified
    if 'fill' not in kwargs:
        kwargs['fill'] = getattr(engine, 'fill_color', None)
    if 'stroke' not in kwargs:
        kwargs['stroke'] = getattr(engine, 'stroke_color', None)
    if 'stroke_weight' not in kwargs:
        kwargs['stroke_weight'] = getattr(engine, 'stroke_weight', 1)
    return engine.graphics.record('point', x=x, y=y, **kwargs)


def begin_shape(engine: Any, mode: str = 'POLYGON'):
    """Begin recording a shape. Subsequent calls to `vertex` will be
    recorded and emitted when `end_shape` is called.
    """
    # initialize a temporary per-engine buffer for shape vertices
    try:
        engine._current_shape = {'mode': str(mode), 'vertices': []}
    except Exception:
        engine._current_shape = {'mode': str(mode), 'vertices': []}
    return engine.graphics.record('begin_shape', mode=str(mode))


def vertex(engine: Any, x: float, y: float):
    """Record a single vertex into the current shape buffer."""
    try:
        buf = getattr(engine, '_current_shape')
        buf['vertices'].append((float(x), float(y)))
    except Exception:
        # If no begin_shape was called, still record the vertex as a standalone op
        return engine.graphics.record('vertex', x=float(x), y=float(y))
    return None


def end_shape(engine: Any, close: bool = False):
    """End the current shape and emit a single 'shape' command with vertices."""
    buf = getattr(engine, '_current_shape', None)
    if buf is None:
        return engine.graphics.record('end_shape', close=bool(close))
    verts = list(buf.get('vertices', []))
    mode = buf.get('mode', 'POLYGON')
    # clear buffer
    try:
        delattr(engine, '_current_shape')
    except Exception:
        try:
            del engine._current_shape
        except Exception:
            pass
    return engine.graphics.record('shape', mode=str(mode), vertices=verts, close=bool(close))
