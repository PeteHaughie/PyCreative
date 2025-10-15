"""fill() API helper: parse args and set engine.fill_color."""
from __future__ import annotations

from typing import Any
from core.color import hsb_to_rgb


def set_fill(engine: Any, *args):
    """Parse `fill()` overloads and set `engine.fill_color` and optional `engine.fill_alpha`.

    Supports gray, rgb, rgb tuple, and optional alpha when engine is offscreen.
    """
    mode = getattr(engine, 'color_mode', 'RGB')

    def _norm(vals):
        if str(mode).upper() == 'HSB':
            return tuple(hsb_to_rgb(*vals))
        return (int(vals[0]), int(vals[1]), int(vals[2]))

    a = None
    if len(args) == 1:
        v = args[0]
        if isinstance(v, (tuple, list)) and len(v) == 3:
            engine.fill_color = tuple(int(x) for x in _norm(v))
            engine.fill_alpha = None
            return
        try:
            iv = int(v)
        except Exception:
            raise TypeError('fill() single arg must be numeric or a 3-tuple')
        engine.fill_color = (iv, iv, iv)
        engine.fill_alpha = None
        return
    elif len(args) == 3:
        engine.fill_color = tuple(int(x) for x in _norm(args))
        engine.fill_alpha = None
        return
    elif len(args) == 2:
        # gray + alpha
        try:
            iv = int(args[0])
            a = float(args[1])
        except Exception:
            raise TypeError('fill(gray, alpha) expects (number, number)')
        # alpha only allowed for offscreen graphics
        if not bool(getattr(engine, '_is_offscreen_graphics', False)):
            raise TypeError('alpha parameter in fill() is allowed only with an offscreen PCGraphics object')
        engine.fill_color = (iv, iv, iv)
        engine.fill_alpha = float(a)
        return
    elif len(args) == 4:
        # r,g,b,alpha
        engine.fill_color = tuple(int(x) for x in _norm(args[:3]))
        try:
            if not bool(getattr(engine, '_is_offscreen_graphics', False)):
                raise TypeError('alpha parameter in fill() is allowed only with an offscreen PCGraphics object')
            engine.fill_alpha = float(args[3])
        except Exception:
            raise TypeError('fill(r,g,b,alpha) alpha must be numeric')
        return
    else:
        raise TypeError('fill() expects 1 or 3 args')
