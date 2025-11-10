"""fill() API helper: parse args and set engine.fill_color."""
from __future__ import annotations

from typing import Any

from core.color import hsb_to_rgb, red as _red, green as _green, blue as _blue, alpha as _alpha


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
                    h_in = float(vals[0])
                    s_in = float(vals[1])
                    v_in = float(vals[2])
                    if h_in <= 1.0 and s_in <= 1.0 and v_in <= 1.0:
                        return tuple(hsb_to_rgb(h_in, s_in, v_in))
                    h = h_in / float(maxs[0])
                    s = s_in / float(maxs[1])
                    v = v_in / float(maxs[2])
                    return tuple(hsb_to_rgb(h, s, v))
                except Exception:
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
        # If engine has a color_mode_max with an explicit alpha maximum,
        # prefer that scaling (e.g., color_mode('HSB',360,100,100,100) ->
        # alpha max is 100). If the user provided a fractional alpha <=1,
        # keep it as-is.
        maxs = getattr(engine, 'color_mode_max', None)
        if maxs is not None and len(maxs) >= 4:
            # If the caller provided a fraction, accept it; otherwise
            # scale by the provided alpha maximum.
            if f > 1.0:
                try:
                    f = f / float(maxs[3])
                except Exception:
                    # fallback to 255-style division if something goes wrong
                    f = f / 255.0
        else:
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
        # Accept an ARGB integer produced by core.color.color() and
        # decompose it into r,g,b,(alpha) so sketches can call
        # fill(self.color(...)) like Processing.
        try:
            if isinstance(v, int):
                r = int(_red(v))
                g = int(_green(v))
                b = int(_blue(v))
                a_byte = int(_alpha(v))
                engine.fill_color = (r, g, b)
                engine.fill_alpha = None if a_byte == 255 else float(a_byte) / 255.0
                return
        except Exception:
            # fall through to existing logic on error
            pass
        if isinstance(v, (tuple, list)) and len(v) == 3:
            # Heuristic: if tuple components look like 0..255 RGB values
            # (any component > 1), treat as raw RGB and don't reinterpret
            # under the current color_mode (which might be HSB). This
            # prevents image.get() RGB tuples from being mistaken for HSB
            # when the sketch has set color_mode('HSB').
            try:
                any_gt_one = any(float(x) > 1.0 for x in v)
            except Exception:
                any_gt_one = False

            if any_gt_one:
                engine.fill_color = tuple(int(x) for x in v)
                engine.fill_alpha = None
                return

            # Fallback: treat as color-mode components (HSB or RGB depending
            # on engine.color_mode) by normalizing through _norm.
            engine.fill_color = tuple(int(x) for x in _norm(v))
            engine.fill_alpha = None
            return
        if isinstance(v, (tuple, list)) and len(v) == 4:
            # accept a single 4-tuple (r,g,b,alpha)
            # Heuristic: if components look like 0..255 RGB values (any > 1)
            # treat as raw RGB; otherwise interpret via current color_mode.
            try:
                any_gt_one = any(float(x) > 1.0 for x in v[:3])
            except Exception:
                any_gt_one = False

            if any_gt_one:
                r, g, b = (int(v[0]), int(v[1]), int(v[2]))
            else:
                r, g, b = _norm(v[:3])
            try:
                a = _norm_alpha(v[3])
            except Exception:
                raise TypeError('fill((r,g,b,a)) expects numeric alpha')
            engine.fill_color = (int(r), int(g), int(b))
            engine.fill_alpha = float(a)
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
        # packed-int color + alpha (Processing allows fill(color, alpha))
        try:
            if isinstance(first, int):
                # decompose packed ARGB int and apply alpha
                r = int(_red(first))
                g = int(_green(first))
                b = int(_blue(first))
                try:
                    a = _norm_alpha(second)
                except Exception:
                    raise TypeError('fill(color, alpha) expects numeric alpha')
                engine.fill_color = (r, g, b)
                engine.fill_alpha = float(a)
                return
        except Exception:
            # fall through to existing logic on error
            pass
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
