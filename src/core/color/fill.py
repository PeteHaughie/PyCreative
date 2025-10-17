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
            # Support optional engine-provided maxima (e.g., color_mode('HSB',360,100,100))
            maxs = getattr(engine, 'color_mode_max', None)
            if maxs is not None and len(maxs) >= 3:
                try:
                    h = float(vals[0]) / float(maxs[0])
                    s = float(vals[1]) / float(maxs[1])
                    v = float(vals[2]) / float(maxs[2])
                    return tuple(hsb_to_rgb(h, s, v))
                except Exception:
                    # Fall back to raw values
                    return tuple(hsb_to_rgb(vals[0], vals[1], vals[2]))
            return tuple(hsb_to_rgb(vals[0], vals[1], vals[2]))
        return (int(vals[0]), int(vals[1]), int(vals[2]))

    a = None

    def _norm_alpha(val):
        """Normalize alpha to 0..1.

        Accepts values in 0..1 or 0..255 (Processing-style). If val > 1
        we assume 0..255 and divide by 255. Values are clamped to [0,1].
        """
        try:
            f = float(val)
        except Exception:
            raise TypeError('alpha must be numeric')
        # If user provided 0..255-style alpha (greater than 1), convert.
        if f > 1.0:
            f = f / 255.0
        # clamp
        if f < 0.0:
            f = 0.0
        if f > 1.0:
            f = 1.0
        return float(f)
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
        # Support two-arg forms: (gray, alpha) OR (rgb_tuple, alpha)
        first, second = args[0], args[1]
        # rgb tuple + alpha
        if isinstance(first, (tuple, list)) and len(first) == 3:
            r, g, b = _norm(first)
            try:
                a = _norm_alpha(second)
            except Exception:
                raise TypeError('fill((r,g,b), alpha) expects numeric alpha')
            # Allow alpha on the main surface for fills; background() remains offscreen-only
            engine.fill_color = (int(r), int(g), int(b))
            engine.fill_alpha = float(a)
            return
        # gray + alpha
        try:
            iv = int(first)
            a = _norm_alpha(second)
        except Exception:
            raise TypeError('fill(gray, alpha) expects (number, number)')
        engine.fill_color = (iv, iv, iv)
        engine.fill_alpha = float(a)
        return
    elif len(args) == 4:
        # r,g,b,alpha
        engine.fill_color = tuple(int(x) for x in _norm(args[:3]))
        try:
            # Allow alpha on fills (main surface); background() is still offscreen-only
            engine.fill_alpha = _norm_alpha(args[3])
        except TypeError:
            raise
        except Exception:
            raise TypeError('fill(r,g,b,alpha) alpha must be numeric')
        return
    else:
        raise TypeError('fill() expects 1 or 3 args')
