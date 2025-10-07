from __future__ import annotations

from typing import List, Tuple


def flatten_cubic_bezier(p0: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float], steps: int = 16) -> List[Tuple[float, float]]:
    """Sample a cubic Bezier curve and return a list of points including endpoints.

    Uses uniform parameter sampling (matches previous implementation in graphics.py).
    """
    pts: list[tuple[float, float]] = []
    steps = max(2, int(steps))
    for i in range(steps + 1):
        t = i / steps
        mt = 1 - t
        x = (mt ** 3) * p0[0] + 3 * (mt ** 2) * t * p1[0] + 3 * mt * (t ** 2) * p2[0] + (t ** 3) * p3[0]
        y = (mt ** 3) * p0[1] + 3 * (mt ** 2) * t * p1[1] + 3 * mt * (t ** 2) * p2[1] + (t ** 3) * p3[1]
        pts.append((x, y))
    return pts


def bezier_point(p0, p1, p2, p3, t: float):
    t = float(t)
    mt = 1.0 - t
    if not hasattr(p0, "__iter__"):
        return (mt ** 3) * p0 + 3 * (mt ** 2) * t * p1 + 3 * mt * (t ** 2) * p2 + (t ** 3) * p3
    x = (mt ** 3) * p0[0] + 3 * (mt ** 2) * t * p1[0] + 3 * mt * (t ** 2) * p2[0] + (t ** 3) * p3[0]
    y = (mt ** 3) * p0[1] + 3 * (mt ** 2) * t * p1[1] + 3 * mt * (t ** 2) * p2[1] + (t ** 3) * p3[1]
    return (x, y)


def bezier_tangent(p0, p1, p2, p3, t: float):
    t = float(t)
    mt = 1.0 - t
    if not hasattr(p0, "__iter__"):
        return 3 * ((p1 - p0) * (mt ** 2) + 2 * (p2 - p1) * mt * t + (p3 - p2) * (t ** 2))
    dx = 3 * ((p1[0] - p0[0]) * (mt ** 2) + 2 * (p2[0] - p1[0]) * mt * t + (p3[0] - p2[0]) * (t ** 2))
    dy = 3 * ((p1[1] - p0[1]) * (mt ** 2) + 2 * (p2[1] - p1[1]) * mt * t + (p3[1] - p2[1]) * (t ** 2))
    return (dx, dy)


def curve_point(p0, p1, p2, p3, t: float, tightness: float = 0.0):
    t = float(t)
    k = (1.0 - float(tightness)) * 0.5

    def _eval_scalar(a, b, c, d):
        m1 = k * (c - a)
        m2 = k * (d - b)
        h00 = (2 * t ** 3) - (3 * t ** 2) + 1
        h10 = (t ** 3) - (2 * t ** 2) + t
        h01 = (-2 * t ** 3) + (3 * t ** 2)
        h11 = (t ** 3) - (t ** 2)
        return h00 * b + h10 * m1 + h01 * c + h11 * m2

    if not hasattr(p0, "__iter__"):
        return _eval_scalar(p0, p1, p2, p3)
    x = _eval_scalar(p0[0], p1[0], p2[0], p3[0])
    y = _eval_scalar(p0[1], p1[1], p2[1], p3[1])
    return (x, y)


def curve_tangent(p0, p1, p2, p3, t: float, tightness: float = 0.0):
    t = float(t)
    k = (1.0 - float(tightness)) * 0.5

    def _eval_scalar_deriv(a, b, c, d):
        m1 = k * (c - a)
        m2 = k * (d - b)
        dh00 = 6 * t ** 2 - 6 * t
        dh10 = 3 * t ** 2 - 4 * t + 1
        dh01 = -6 * t ** 2 + 6 * t
        dh11 = 3 * t ** 2 - 2 * t
        return dh00 * b + dh10 * m1 + dh01 * c + dh11 * m2

    if not hasattr(p0, "__iter__"):
        return _eval_scalar_deriv(p0, p1, p2, p3)
    dx = _eval_scalar_deriv(p0[0], p1[0], p2[0], p3[0])
    dy = _eval_scalar_deriv(p0[1], p1[1], p2[1], p3[1])
    return (dx, dy)
