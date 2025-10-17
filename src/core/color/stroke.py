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
            maxs = getattr(engine, 'color_mode_max', None)
            if maxs is not None and len(maxs) >= 3:
                try:
                    h = float(vals[0]) / float(maxs[0])
                    s = float(vals[1]) / float(maxs[1])
                    v = float(vals[2]) / float(maxs[2])
                    return tuple(hsb_to_rgb(h, s, v))
                except Exception:
                    return tuple(hsb_to_rgb(vals[0], vals[1], vals[2]))
            return tuple(hsb_to_rgb(vals[0], vals[1], vals[2]))
        return (int(vals[0]), int(vals[1]), int(vals[2]))

    a = None

    def _norm_alpha(val):
        """Normalize alpha to 0..1. Accept 0..1 or 0..255 and clamp."""
        try:
            f = float(val)
        except Exception:
            raise TypeError('alpha must be numeric')
        if f > 1.0:
            f = f / 255.0
        if f < 0.0:
            f = 0.0
        if f > 1.0:
            f = 1.0
        return float(f)
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
        # Support (gray, alpha) or ((r,g,b), alpha)
        first, second = args[0], args[1]
        if isinstance(first, (tuple, list)) and len(first) == 3:
            try:
                a = _norm_alpha(second)
            except Exception:
                raise TypeError('stroke((r,g,b), alpha) expects numeric alpha')
            engine.stroke_color = tuple(int(x) for x in _norm(first))
            engine.stroke_alpha = float(a)
            return
        try:
            iv = int(first)
            a = _norm_alpha(second)
        except Exception:
            raise TypeError('stroke(gray, alpha) expects (number, number)')
        engine.stroke_color = (iv, iv, iv)
        engine.stroke_alpha = float(a)
        return
    elif len(args) == 4:
        engine.stroke_color = tuple(int(x) for x in _norm(args[:3]))
        try:
            # Allow alpha on strokes (main surface)
            engine.stroke_alpha = _norm_alpha(args[3])
        except TypeError:
            raise
        except Exception:
            raise TypeError('stroke(r,g,b,alpha) alpha must be numeric')
        return
    else:
        raise TypeError('stroke() expects 1 or 3 args')
