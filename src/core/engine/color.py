"""Color helpers for the engine (HSB/HSV <-> RGB conversion).

Pure functions with no side effects so they can be tested independently.
"""
from typing import Tuple


def hsb_to_rgb(h: float, s: float, b: float) -> Tuple[int, int, int]:
    """Convert HSB/HSV to RGB.

    Accepts either 0-1 floats or 0-255 ints for each component. Returns a
    tuple of ints in 0-255.
    """
    def norm(v: float) -> float:
        return v / 255.0 if v > 1 else float(v)

    H = norm(h)
    S = norm(s)
    V = norm(b)

    if S == 0:
        val = int(round(V * 255))
        return (val, val, val)

    i = int(H * 6)  # sector 0..5
    f = (H * 6) - i
    p = V * (1 - S)
    q = V * (1 - S * f)
    t = V * (1 - S * (1 - f))

    i = i % 6
    if i == 0:
        r_, g_, b_ = V, t, p
    elif i == 1:
        r_, g_, b_ = q, V, p
    elif i == 2:
        r_, g_, b_ = p, V, t
    elif i == 3:
        r_, g_, b_ = p, q, V
    elif i == 4:
        r_, g_, b_ = t, p, V
    else:
        r_, g_, b_ = V, p, q

    return (int(round(r_ * 255)), int(round(g_ * 255)), int(round(b_ * 255)))
