import math
from pycreative.vector import PVector


def test_basic_arithmetic_and_copy():
    a = PVector(1, 2)
    b = a.copy()
    assert a.x == b.x and a.y == b.y
    c = a + PVector(3, 4)
    assert (c.x, c.y) == (4, 6)
    d = c - (1, 1)
    assert (d.x, d.y) == (3, 5)


def test_mutating_ops_and_mag():
    v = PVector(3, 4)
    assert math.isclose(v.mag(), 5.0)
    v.normalize()
    assert math.isclose(v.mag(), 1.0)
    v.set_mag(10)
    assert math.isclose(v.mag(), 10.0)


def test_limit_and_rotate():
    v = PVector(10, 0)
    v.limit(5)
    assert math.isclose(v.mag(), 5.0)
    v = PVector(1, 0)
    v.rotate(math.pi / 2)
    assert abs(v.x) < 1e-6 and abs(v.y - 1) < 1e-6


def test_lerp_and_dist():
    v = PVector(0, 0)
    v.lerp(PVector(10, 0), 0.5)
    assert math.isclose(v.x, 5.0)
    assert math.isclose(v.dist(PVector(5, 0)), 0.0)
