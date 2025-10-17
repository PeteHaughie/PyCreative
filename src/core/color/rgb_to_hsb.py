"""RGB -> HSB conversion helper.

Pure and small to make testing and reasoning easy.
"""
from typing import Tuple


def rgb_to_hsb(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """Convert RGB to HSB/HSV.

    Accepts either 0-1 floats or 0-255 ints for each component. Returns a
    tuple (h, s, v) with floats in the 0..1 range. For grayscale colors the
    hue is returned as 0.0.
    """
    def norm(vv: float) -> float:
        return vv / 255.0 if vv > 1 else float(vv)

    R = norm(r)
    G = norm(g)
    B = norm(b)

    mx = max(R, G, B)
    mn = min(R, G, B)
    v = mx
    delta = mx - mn

    s = 0.0 if mx == 0 else (delta / mx)

    if delta == 0:
        h = 0.0
    else:
        if mx == R:
            h_raw = (G - B) / delta
        elif mx == G:
            h_raw = (B - R) / delta + 2.0
        else:
            h_raw = (R - G) / delta + 4.0

        h = (h_raw / 6.0) % 1.0

    return (float(h), float(s), float(v))
