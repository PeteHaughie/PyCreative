"""Shape helpers: small, engine-aware functions for recording shape ops.

These functions accept an `engine` as the first argument to remain
implementation-focused and avoid import-time cycles with the Engine.
"""
from typing import Any
from typing import Optional
import logging

logger = logging.getLogger(__name__)


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


def _triangle_fan(engine: Any, cx: float, cy: float, radius: float, segments: int = 36, start_angle: float = 0.0):
    """Internal helper: record a TRIANGLE_FAN around a center using `segments` slices.

    Kept internal (prefixed with underscore) so it does not expand the public
    sketch API. Presenters or higher-level callers within `core.shape` may
    call this helper when building fan geometry.
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
            # record as a single-triangle shape for simplicity
            engine.graphics.record('shape', mode='TRIANGLES', vertices=[(float(cx), float(cy)), (x1, y1), (x2, y2)], close=False)
    except Exception:
        # best-effort: record nothing on error
        pass


def begin_shape(engine: Any, mode: str = 'POLYGON'):
    """Begin recording a shape. Subsequent calls to `vertex` will be
    recorded and emitted when `end_shape` is called.
    """
    # initialize a temporary per-engine buffer for shape vertices
    # Validate and normalize mode
    allowed_modes = {'POINTS', 'LINES', 'TRIANGLES', 'TRIANGLE_STRIP', 'TRIANGLE_FAN', 'POLYGON'}
    try:
        m = str(mode).upper()
    except Exception:
        m = 'POLYGON'
    if m not in allowed_modes:
        # fallback to POLYGON but record that an unsupported mode was requested
        try:
            engine.graphics.record('unsupported_shape_mode', requested=mode)
        except Exception:
            pass
        m = 'POLYGON'
    try:
        engine._current_shape = {'mode': m, 'vertices': []}
    except Exception:
        engine._current_shape = {'mode': m, 'vertices': []}
    return engine.graphics.record('begin_shape', mode=m)


def vertex(engine: Any, x: float, y: float):
    """Record a single vertex into the current shape buffer."""
    try:
        buf = getattr(engine, '_current_shape')
        if buf is None:
            raise AttributeError
        # capture the current fill color and alpha at the time the vertex
        # was emitted so per-vertex colours are preserved in recorded shapes
        cur_fill = getattr(engine, 'fill_color', None)
        cur_fill_alpha = getattr(engine, 'fill_alpha', None)
        buf['vertices'].append((float(x), float(y), cur_fill, cur_fill_alpha))
    except Exception:
        # If no begin_shape was called, log a warning and record a standalone vertex
        try:
            logger.warning('vertex called outside begin_shape; recording standalone vertex')
        except Exception:
            pass
        return engine.graphics.record('vertex', x=float(x), y=float(y))
    return None


def end_shape(engine: Any, close: bool = False):
    """End the current shape and emit a single 'shape' command with vertices."""
    buf = getattr(engine, '_current_shape', None)
    if buf is None:
        return engine.graphics.record('end_shape', close=bool(close))
    verts = list(buf.get('vertices', []))
    mode = buf.get('mode', 'POLYGON')
    # Basic validation for certain modes to catch obvious user errors.
    # Instead of raising, record an 'invalid_shape' command so headless tests
    # and presenters can surface an error without breaking sketch execution.
    try:
        vcount = len(verts)
        if mode == 'LINES' and (vcount % 2) != 0:
            try:
                logger.warning('invalid shape: LINES requires even number of vertices')
            except Exception:
                pass
            return engine.graphics.record('invalid_shape', reason='LINES requires even number of vertices', mode=mode, vertices=verts)
        if mode == 'TRIANGLES' and (vcount % 3) != 0:
            try:
                logger.warning('invalid shape: TRIANGLES requires vertex count multiple of 3')
            except Exception:
                pass
            return engine.graphics.record('invalid_shape', reason='TRIANGLES requires vertices count multiple of 3', mode=mode, vertices=verts)
        if mode == 'POINTS' and vcount == 0:
            try:
                logger.warning('invalid shape: POINTS requires at least one vertex')
            except Exception:
                pass
            return engine.graphics.record('invalid_shape', reason='POINTS requires at least one vertex', mode=mode, vertices=verts)
    except Exception:
        # best-effort: continue to record shape
        pass
    # If per-vertex colors were recorded (vertex entries are 4-tuples), we
    # can preserve per-vertex fill by emitting individual triangle records
    # for TRIANGLE_FAN mode so painters that don't support vertex interpolation
    # can still display per-triangle colours.
    try:
        # detect whether vertices include per-vertex color tuples
        has_vertex_color = False
        if len(verts) > 0 and isinstance(verts[0], (list, tuple)) and len(verts[0]) >= 3:
            has_vertex_color = True
    except Exception:
        has_vertex_color = False

    # For TRIANGLE_FAN with per-vertex colors, emit per-triangle 'shape'
    # commands with an attached fill so the replayer can render them.
    try:
        if mode == 'TRIANGLE_FAN' and has_vertex_color and len(verts) >= 3:
            # verts entries are (x,y,fill,fill_alpha). First vert is center.
            v0 = verts[0]
            for i in range(1, len(verts) - 1):
                a = verts[i]
                b = verts[i + 1]
                # choose fill for this triangle: prefer outer vertex a's fill,
                # fallback to b's fill, then engine.fill_color
                tri_fill = a[2] if a[2] is not None else (b[2] if b[2] is not None else getattr(engine, 'fill_color', None))
                tri_alpha = a[3] if a[3] is not None else (b[3] if b[3] is not None else getattr(engine, 'fill_alpha', None))
                # vertices for this triangle: center, a, b
                tri_verts = [(float(v0[0]), float(v0[1])), (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))]
                # record a small TRIANGLES-shaped command with a per-triangle fill
                try:
                    engine.graphics.record('shape', mode='TRIANGLES', vertices=tri_verts, fill=tri_fill, fill_alpha=tri_alpha, close=False)
                except Exception:
                    try:
                        engine.graphics.record('shape', mode='TRIANGLES', vertices=tri_verts, close=False)
                    except Exception:
                        pass
            # clear and return after emitting all triangles
            try:
                delattr(engine, '_current_shape')
            except Exception:
                try:
                    del engine._current_shape
                except Exception:
                    pass
            return None
    except Exception:
        # fall through to default behaviour on error
        pass

    # clear buffer
    try:
        delattr(engine, '_current_shape')
    except Exception:
        try:
            del engine._current_shape
        except Exception:
            pass
    return engine.graphics.record('shape', mode=str(mode), vertices=verts, close=bool(close))
