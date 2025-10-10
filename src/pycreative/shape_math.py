from __future__ import annotations

from typing import List, Tuple, Union


def flatten_cubic_bezier(p0: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float], steps: int = 16, tol: float = 0.5) -> List[Tuple[float, float]]:
    """Flatten a cubic Bezier adaptively using recursive subdivision.

    Returns a list of points including endpoints. The `steps` parameter is
    interpreted as a hint for maximum recursion depth when needed. `tol` is
    the flatness tolerance in pixels — smaller values produce denser output.
    """
    import math

    def _dist_point_line(px, py, x0, y0, x1, y1):
        # distance from point to line segment (x0,y0)-(x1,y1)
        dx = x1 - x0
        dy = y1 - y0
        if dx == 0 and dy == 0:
            return math.hypot(px - x0, py - y0)
        t = ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)
        # project (not clamped) for flatness test
        projx = x0 + t * dx
        projy = y0 + t * dy
        return math.hypot(px - projx, py - projy)

    def _is_flat(p0, p1, p2, p3):
        # estimate flatness by distance of control points to chord p0-p3
        d1 = _dist_point_line(p1[0], p1[1], p0[0], p0[1], p3[0], p3[1])
        d2 = _dist_point_line(p2[0], p2[1], p0[0], p0[1], p3[0], p3[1])
        return max(d1, d2) <= float(tol)

    def _subdivide(p0, p1, p2, p3, depth):
        if depth <= 0 or _is_flat(p0, p1, p2, p3):
            return [p0, p3]
        # de Casteljau subdivision
        m01 = ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0)
        m12 = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
        m23 = ((p2[0] + p3[0]) / 2.0, (p2[1] + p3[1]) / 2.0)
        m012 = ((m01[0] + m12[0]) / 2.0, (m01[1] + m12[1]) / 2.0)
        m123 = ((m12[0] + m23[0]) / 2.0, (m12[1] + m23[1]) / 2.0)
        m = ((m012[0] + m123[0]) / 2.0, (m012[1] + m123[1]) / 2.0)
        left = _subdivide(p0, m01, m012, m, depth - 1)
        right = _subdivide(m, m123, m23, p3, depth - 1)
        # stitch without duplicating the middle point
        return left[:-1] + right

    max_depth = max(4, int(steps))
    pts = _subdivide(p0, p1, p2, p3, max_depth)
    return pts


def flatten_quadratic_bezier(p0: Tuple[float, float], p1: Tuple[float, float], p2: Tuple[float, float], steps: int = 16, tol: float = 0.5) -> List[Tuple[float, float]]:
    """Flatten a quadratic Bezier using adaptive subdivision.

    `tol` is the flatness tolerance in pixels — smaller values produce denser output.
    """
    import math

    def _dist_point_line(px, py, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        if dx == 0 and dy == 0:
            return math.hypot(px - x0, py - y0)
        t = ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)
        projx = x0 + t * dx
        projy = y0 + t * dy
        return math.hypot(px - projx, py - projy)

    def _is_flat(p0, p1, p2):
        d = _dist_point_line(p1[0], p1[1], p0[0], p0[1], p2[0], p2[1])
        return d <= float(tol)

    def _subdivide(p0, p1, p2, depth):
        if depth <= 0 or _is_flat(p0, p1, p2):
            return [p0, p2]
        # subdivide
        m01 = ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0)
        m12 = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
        m = ((m01[0] + m12[0]) / 2.0, (m01[1] + m12[1]) / 2.0)
        left = _subdivide(p0, m01, m, depth - 1)
        right = _subdivide(m, m12, p2, depth - 1)
        return left[:-1] + right

    max_depth = max(4, int(steps))
    return _subdivide(p0, p1, p2, max_depth)


def flatten_arc(p0: Tuple[float, float], p1: Tuple[float, float], rx: float, ry: float, x_axis_rotation: float, large_arc_flag: int, sweep_flag: int, steps: int = 24) -> List[Tuple[float, float]]:
    """Flatten an SVG elliptical arc from p0 to p1 using the endpoint parameterization.

    This implements the conversion to center parameterization per the SVG spec
    and samples the arc uniformly in angle. Returns a list of points including
    start and end.
    """
    import math

    x1, y1 = p0
    x2, y2 = p1
    # handle degenerate arc
    if rx == 0 or ry == 0:
        return [p0, p1]

    # convert rotation to radians
    phi = math.radians(x_axis_rotation % 360.0)
    cos_phi = math.cos(phi)
    sin_phi = math.sin(phi)

    # Step 1: compute (x1', y1')
    dx2 = (x1 - x2) / 2.0
    dy2 = (y1 - y2) / 2.0
    x1p = cos_phi * dx2 + sin_phi * dy2
    y1p = -sin_phi * dx2 + cos_phi * dy2

    # Ensure radii are large enough
    rx = abs(rx)
    ry = abs(ry)
    # Correct out-of-range radii
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        s = math.sqrt(lam)
        rx *= s
        ry *= s

    # Step 2: compute center
    denom = (rx * rx) * (y1p * y1p) + (ry * ry) * (x1p * x1p)
    # numeric guard
    if denom == 0:
        return [p0, p1]

    num = (rx * rx) * (ry * ry) - (rx * rx) * (y1p * y1p) - (ry * ry) * (x1p * x1p)
    num = max(0.0, num)
    factor = math.sqrt(num / denom)
    if large_arc_flag == sweep_flag:
        factor = -factor

    cxp = factor * (rx * y1p) / ry
    cyp = factor * (-ry * x1p) / rx

    # Step 3: center in original coords
    cx = cos_phi * cxp - sin_phi * cyp + (x1 + x2) / 2.0
    cy = sin_phi * cxp + cos_phi * cyp + (y1 + y2) / 2.0

    # Step 4: compute start and delta angles
    def angle(u, v):
        # angle between 2D vectors
        ux, uy = u
        vx, vy = v
        dot = ux * vx + uy * vy
        mag = math.hypot(ux, uy) * math.hypot(vx, vy)
        if mag == 0:
            return 0.0
        a = max(-1.0, min(1.0, dot / mag))
        sign = 1.0 if (ux * vy - uy * vx) >= 0 else -1.0
        return sign * math.acos(a)

    ux = (x1p - cxp) / rx
    uy = (y1p - cyp) / ry
    vx = (-x1p - cxp) / rx
    vy = (-y1p - cyp) / ry

    theta1 = angle((1.0, 0.0), (ux, uy))
    delta = angle((ux, uy), (vx, vy))

    # Ensure correct sweep
    if sweep_flag == 0 and delta > 0:
        delta -= 2 * math.pi
    elif sweep_flag == 1 and delta < 0:
        delta += 2 * math.pi

    # sample points along the arc
    total_steps = max(2, int(math.ceil(abs(delta) / (math.pi / 24.0))))
    pts: list[tuple[float, float]] = []
    for i in range(total_steps + 1):
        t = theta1 + (delta * i) / total_steps
        cos_t = math.cos(t)
        sin_t = math.sin(t)
        x = cx + rx * cos_phi * cos_t - ry * sin_phi * sin_t
        y = cy + rx * sin_phi * cos_t + ry * cos_phi * sin_t
        pts.append((x, y))
    return pts


def bezier_point(p0: Union[float, Tuple[float, float]], p1: Union[float, Tuple[float, float]], p2: Union[float, Tuple[float, float]], p3: Union[float, Tuple[float, float]], t: float) -> Union[float, Tuple[float, float]]:
    t = float(t)
    mt = 1.0 - t
    if not isinstance(p0, (list, tuple)):
        # scalar variant: tell mypy these are floats
        from typing import cast
        p0s = cast(float, p0)
        p1s = cast(float, p1)
        p2s = cast(float, p2)
        p3s = cast(float, p3)
        return (mt ** 3) * p0s + 3 * (mt ** 2) * t * p1s + 3 * mt * (t ** 2) * p2s + (t ** 3) * p3s
    # sequence variant (assume 2D tuple)
    assert isinstance(p1, (list, tuple)) and isinstance(p2, (list, tuple)) and isinstance(p3, (list, tuple))
    p0x, p0y = p0[0], p0[1]
    p1x, p1y = p1[0], p1[1]
    p2x, p2y = p2[0], p2[1]
    p3x, p3y = p3[0], p3[1]
    x = (mt ** 3) * p0x + 3 * (mt ** 2) * t * p1x + 3 * mt * (t ** 2) * p2x + (t ** 3) * p3x
    y = (mt ** 3) * p0y + 3 * (mt ** 2) * t * p1y + 3 * mt * (t ** 2) * p2y + (t ** 3) * p3y
    return (x, y)


def bezier_tangent(p0: Union[float, Tuple[float, float]], p1: Union[float, Tuple[float, float]], p2: Union[float, Tuple[float, float]], p3: Union[float, Tuple[float, float]], t: float) -> Union[float, Tuple[float, float]]:
    t = float(t)
    mt = 1.0 - t
    if not isinstance(p0, (list, tuple)):
        from typing import cast
        p0s = cast(float, p0)
        p1s = cast(float, p1)
        p2s = cast(float, p2)
        p3s = cast(float, p3)
        return 3 * ((p1s - p0s) * (mt ** 2) + 2 * (p2s - p1s) * mt * t + (p3s - p2s) * (t ** 2))
    assert isinstance(p1, (list, tuple)) and isinstance(p2, (list, tuple)) and isinstance(p3, (list, tuple))
    dx = 3 * ((p1[0] - p0[0]) * (mt ** 2) + 2 * (p2[0] - p1[0]) * mt * t + (p3[0] - p2[0]) * (t ** 2))
    dy = 3 * ((p1[1] - p0[1]) * (mt ** 2) + 2 * (p2[1] - p1[1]) * mt * t + (p3[1] - p2[1]) * (t ** 2))
    return (dx, dy)


def curve_point(p0: Union[float, Tuple[float, float]], p1: Union[float, Tuple[float, float]], p2: Union[float, Tuple[float, float]], p3: Union[float, Tuple[float, float]], t: float, tightness: float = 0.0) -> Union[float, Tuple[float, float]]:
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

    if not isinstance(p0, (list, tuple)):
        return _eval_scalar(p0, p1, p2, p3)
    assert isinstance(p1, (list, tuple)) and isinstance(p2, (list, tuple)) and isinstance(p3, (list, tuple))
    x = _eval_scalar(p0[0], p1[0], p2[0], p3[0])
    y = _eval_scalar(p0[1], p1[1], p2[1], p3[1])
    return (x, y)


def curve_tangent(p0: Union[float, Tuple[float, float]], p1: Union[float, Tuple[float, float]], p2: Union[float, Tuple[float, float]], p3: Union[float, Tuple[float, float]], t: float, tightness: float = 0.0) -> Union[float, Tuple[float, float]]:
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

    if not isinstance(p0, (list, tuple)):
        return _eval_scalar_deriv(p0, p1, p2, p3)
    assert isinstance(p1, (list, tuple)) and isinstance(p2, (list, tuple)) and isinstance(p3, (list, tuple))
    dx = _eval_scalar_deriv(p0[0], p1[0], p2[0], p3[0])
    dy = _eval_scalar_deriv(p0[1], p1[1], p2[1], p3[1])
    return (dx, dy)
