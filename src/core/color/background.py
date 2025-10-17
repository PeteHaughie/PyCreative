"""Background() API implementation extracted from SimpleSketchAPI.

This module provides a single function `set_background(engine, *args)` which
parses the various overloads and records the appropriate graphics command.
"""
from __future__ import annotations

from typing import Any
from core.color import hsb_to_rgb


def set_background(engine: Any, *args):
    """Parse `background()` overloads and record background commands on engine.graphics.

    Supports grayscale, RGB, tuple, optional alpha (offscreen only), and image-like objects.
    """
    mode = getattr(engine, 'color_mode', 'RGB')

    def _norm_rgb_from_vals(vals):
        if str(mode).upper() == 'HSB':
            maxs = getattr(engine, 'color_mode_max', None)
            if maxs is not None and len(maxs) >= 3:
                try:
                    h = float(vals[0]) / float(maxs[0])
                    s = float(vals[1]) / float(maxs[1])
                    v = float(vals[2]) / float(maxs[2])
                    r, g, b = hsb_to_rgb(h, s, v)
                except Exception:
                    r, g, b = hsb_to_rgb(vals[0], vals[1], vals[2])
            else:
                r, g, b = hsb_to_rgb(vals[0], vals[1], vals[2])
        else:
            r, g, b = (int(vals[0]), int(vals[1]), int(vals[2]))
        return int(r), int(g), int(b)

    # Image case
    if len(args) == 1:
        v = args[0]
        if hasattr(v, 'size') or (hasattr(v, 'width') and hasattr(v, 'height')):
            try:
                engine.graphics.record('background_image', image=v)
            except Exception:
                engine.graphics.record('background', r=200, g=200, b=200)
            return

    r = g = b = None
    a = None
    if len(args) == 1:
        v = args[0]
        if isinstance(v, (tuple, list)) and len(v) == 3:
            r, g, b = _norm_rgb_from_vals(v)
        else:
            try:
                iv = int(v)
            except Exception:
                raise TypeError('background() single argument must be numeric or a 3-tuple')
            r = g = b = iv
    elif len(args) == 2:
        try:
            iv = int(args[0])
            a = float(args[1])
        except Exception:
            raise TypeError('background(gray, alpha) expects (number, number)')
        r = g = b = iv
    elif len(args) == 3:
        r, g, b = _norm_rgb_from_vals(args)
    elif len(args) == 4:
        r, g, b = _norm_rgb_from_vals(args[:3])
        try:
            a = float(args[3])
        except Exception:
            raise TypeError('background(r,g,b,alpha) alpha must be numeric')
    else:
        raise TypeError('background() expects 1-4 args or an image')

    if a is not None:
        if not bool(getattr(engine, '_is_offscreen_graphics', False)):
            raise TypeError('alpha parameter in background() is allowed only with an offscreen PCGraphics object')

    r = int(max(0, min(255, int(r))))
    g = int(max(0, min(255, int(g))))
    b = int(max(0, min(255, int(b))))

    engine.background_color = (r, g, b)
    try:
        if a is None:
            engine.graphics.record('background', r=r, g=g, b=b)
        else:
            engine.graphics.record('background', r=r, g=g, b=b, a=float(a))
    except Exception:
        pass
