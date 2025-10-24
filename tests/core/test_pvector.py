import math
import pytest

from core.math import PCVector


def approx(a, b, eps=1e-6):
    return abs(a - b) <= eps


def test_mag_and_copy():
    v = PCVector(3, 4)
    assert approx(v.mag(), 5.0)
    c = v.copy()
    assert c == v and c is not v


def test_add_sub_non_mutating_and_ops():
    a = PCVector(1, 2)
    b = PCVector(3, 4)
    s = PCVector.add_vec(a, b)
    assert isinstance(s, PCVector)
    assert s.x == 4 and s.y == 6
    # operator + should return new vector
    c = a + b
    assert c == PCVector(4, 6)
    # operator -
    assert (b - a) == PCVector(2, 2)


def test_inplace_add_sub_mult_div_and_scalar():
    v = PCVector(2, 3)
    v.add((1, 1))
    assert v == PCVector(3, 4)
    v.sub((1, 2))
    assert v == PCVector(2, 2)
    v.mult(2)
    assert v == PCVector(4, 4)
    v.div(2)
    assert v == PCVector(2, 2)


def test_mult_div_with_vector_and_zero_division():
    a = PCVector(2, 6)
    b = PCVector(2, 3)
    r = PCVector.mult_vec(a, b)
    assert r == PCVector(4, 18)
    # division by scalar zero
    with pytest.raises(ZeroDivisionError):
        PCVector.div_vec(a, 0)
    # division by vector with zero component
    with pytest.raises(ZeroDivisionError):
        PCVector.div_vec(a, PCVector(0, 1))


def test_from_angle_and_random2d():
    v = PCVector.from_angle(0.0, 1.0)
    assert approx(v.x, 1.0)
    assert approx(v.y, 0.0)
    r = PCVector.random2d(2.0)
    assert isinstance(r, PCVector)
    assert r.mag() > 0


def test_normalize_set_mag_limit():
    v = PCVector(3, 4)
    v.normalize()
    assert approx(v.mag(), 1.0)
    v.set_mag(5.0)
    assert approx(v.mag(), 5.0)
    v.limit(2.0)
    assert v.mag() <= 2.0 + 1e-6


def test_dot_heading_rotate_lerp():
    a = PCVector(1, 0)
    b = PCVector(0, 1)
    assert approx(a.dot(b), 0.0)
    assert approx(a.heading(), 0.0)
    a.rotate(math.pi / 2)
    assert approx(round(a.x, 6), 0.0)
    # lerp
    p = PCVector(0, 0)
    q = PCVector(10, 0)
    p.lerp(q, 0.5)
    assert approx(p.x, 5.0)


def test_neg_eq_and_tuples():
    a = PCVector(1, 2)
    assert (-a) == PCVector(-1, -2)
    assert a.to_tuple() == (1.0, 2.0)
