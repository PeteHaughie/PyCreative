from typing import Tuple

from pycreative.shape_math import (
    flatten_cubic_bezier,
    flatten_quadratic_bezier,
    flatten_arc,
)


def approx_eq(a: Tuple[float, float], b: Tuple[float, float], eps: float = 1e-6) -> bool:
    return abs(a[0] - b[0]) <= eps and abs(a[1] - b[1]) <= eps


def test_flatten_cubic_preserves_endpoints():
    p0 = (0.0, 0.0)
    p1 = (10.0, 0.0)
    p2 = (10.0, 10.0)
    p3 = (20.0, 10.0)
    pts = flatten_cubic_bezier(p0, p1, p2, p3, steps=8)
    assert pts[0] == p0
    assert pts[-1] == p3
    # expect at least the endpoints plus some intermediates
    assert len(pts) >= 3


def test_flatten_quadratic_preserves_endpoints():
    p0 = (0.0, 0.0)
    p1 = (10.0, 20.0)
    p2 = (20.0, 0.0)
    pts = flatten_quadratic_bezier(p0, p1, p2, steps=8)
    assert pts[0] == p0
    assert pts[-1] == p2
    assert len(pts) >= 3


def test_flatten_arc_basic():
    # quarter circle from (1,0) to (0,1) with rx=ry=1 centered at origin rotated 0
    p0 = (1.0, 0.0)
    p1 = (0.0, 1.0)
    pts = flatten_arc(p0, p1, 1.0, 1.0, 0.0, 0, 1)
    # endpoints preserved approximately
    assert approx_eq(pts[0], p0)
    assert approx_eq(pts[-1], p1)
    # should be multiple points (more than 2)
    assert len(pts) >= 3
