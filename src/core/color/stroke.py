"""stroke() API helper: parse args and set engine.stroke_color."""
from __future__ import annotations

from typing import Any
from core.color import hsb_to_rgb


def set_stroke(engine: Any, *args):
    """Parse `stroke()` overloads and set `engine.stroke_color` and optional `engine.stroke_alpha`.

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
            engine.stroke_color = tuple(int(x) for x in _norm(v))
            engine.stroke_alpha = None
            return
        try:
            iv = int(v)
        except Exception:
            raise TypeError('stroke() single arg must be numeric or a 3-tuple')
        engine.stroke_color = (iv, iv, iv)
        engine.stroke_alpha = None
        return
    elif len(args) == 3:
        engine.stroke_color = tuple(int(x) for x in _norm(args))
        engine.stroke_alpha = None
        return
    elif len(args) == 2:
        try:
            iv = int(args[0])
            a = float(args[1])
        except Exception:
            raise TypeError('stroke(gray, alpha) expects (number, number)')
        if not bool(getattr(engine, '_is_offscreen_graphics', False)):
            raise TypeError('alpha parameter in stroke() is allowed only with an offscreen PCGraphics object')
        engine.stroke_color = (iv, iv, iv)
        engine.stroke_alpha = float(a)
        return
    elif len(args) == 4:
        engine.stroke_color = tuple(int(x) for x in _norm(args[:3]))
        try:
            if not bool(getattr(engine, '_is_offscreen_graphics', False)):
                raise TypeError('alpha parameter in stroke() is allowed only with an offscreen PCGraphics object')
            engine.stroke_alpha = float(args[3])
        except Exception:
            raise TypeError('stroke(r,g,b,alpha) alpha must be numeric')
        return
    else:
        raise TypeError('stroke() expects 1 or 3 args')
