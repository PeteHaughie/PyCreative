"""Shape helpers: small, engine-aware functions for recording shape ops.

These functions accept an `engine` as the first argument to remain
implementation-focused and avoid import-time cycles with the Engine.
"""
from typing import Any


def rect(engine: Any, x: float, y: float, w: float, h: float, **kwargs):
    """Record a rectangle draw command on the engine's graphics buffer."""
    # forward drawing state if not specified
    if 'fill' not in kwargs:
        kwargs['fill'] = getattr(engine, 'fill_color', None)
    if 'stroke' not in kwargs:
        kwargs['stroke'] = getattr(engine, 'stroke_color', None)
    if 'stroke_weight' not in kwargs:
        kwargs['stroke_weight'] = getattr(engine, 'stroke_weight', 1)
    return engine.graphics.record('rect', x=x, y=y, w=w, h=h, **kwargs)


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
