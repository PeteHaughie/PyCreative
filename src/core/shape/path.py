"""Path and complex shape helpers: begin_shape/vertex/end_shape handling.

This module manages a per-engine temporary buffer (`_current_shape`) and
emits a single 'shape' command on `engine.graphics` when `end_shape` is
called. It preserves per-vertex fill information so presenters can render
per-vertex colours where supported.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def begin_shape(engine: Any, mode: str = 'POLYGON'):
    """Begin recording a shape. Subsequent calls to `vertex` will be
    recorded and emitted when `end_shape` is called.
    """
    allowed_modes = {'POINTS', 'LINES', 'TRIANGLES', 'TRIANGLE_STRIP', 'TRIANGLE_FAN', 'POLYGON'}
    try:
        m = str(mode).upper()
    except Exception:
        m = 'POLYGON'
    if m not in allowed_modes:
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
        cur_fill = getattr(engine, 'fill_color', None)
        cur_fill_alpha = getattr(engine, 'fill_alpha', None)
        buf['vertices'].append((float(x), float(y), cur_fill, cur_fill_alpha))
    except Exception:
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
        pass

    try:
        has_vertex_color = False
        if len(verts) > 0 and isinstance(verts[0], (list, tuple)) and len(verts[0]) >= 3:
            has_vertex_color = True
    except Exception:
        has_vertex_color = False

    try:
        if mode == 'TRIANGLE_FAN' and has_vertex_color and len(verts) >= 3:
            v0 = verts[0]
            for i in range(1, len(verts) - 1):
                a = verts[i]
                b = verts[i + 1]
                tri_fill = a[2] if a[2] is not None else (b[2] if b[2] is not None else getattr(engine, 'fill_color', None))
                tri_alpha = a[3] if a[3] is not None else (b[3] if b[3] is not None else getattr(engine, 'fill_alpha', None))
                tri_verts = [(float(v0[0]), float(v0[1])), (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))]
                try:
                    engine.graphics.record('shape', mode='TRIANGLES', vertices=tri_verts, fill=tri_fill, fill_alpha=tri_alpha, close=False)
                except Exception:
                    try:
                        engine.graphics.record('shape', mode='TRIANGLES', vertices=tri_verts, close=False)
                    except Exception:
                        pass
            try:
                delattr(engine, '_current_shape')
            except Exception:
                try:
                    del engine._current_shape
                except Exception:
                    pass
            return None
    except Exception:
        pass

    try:
        delattr(engine, '_current_shape')
    except Exception:
        try:
            del engine._current_shape
        except Exception:
            pass
    return engine.graphics.record('shape', mode=str(mode), vertices=verts, close=bool(close))
