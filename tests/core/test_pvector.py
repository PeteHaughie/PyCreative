import math
import pytest
from core.math import PCVector, lerp


def test_basic_creation_and_tuple():
    v = PCVector(3, 4)
    assert v.to_tuple() == (3.0, 4.0)
    assert v.mag() == 5.0


def test_copy_and_equality():
    v = PCVector(1.5, -2.0)
    c = v.copy()
    assert c == v
    c.x = 0
    assert c != v


def test_add_sub_and_operators():
    a = PCVector(1, 2)
    b = PCVector(3, 4)
    a.add(b)
    assert a == PCVector(4, 6)
    c = a - PCVector(1, 1)
    assert c == PCVector(3, 5)
    d = c + 2
    assert d == PCVector(5, 7)


def test_mult_div_and_componentwise():
    v = PCVector(2, 3)
    v.mult(2)
    assert v == PCVector(4, 6)
    v.div(2)
    assert v == PCVector(2, 3)
    v2 = PCVector(10, 5)
    v3 = v * 2
    assert v3 == PCVector(4, 6)
    v4 = v2 / 5
    assert v4 == PCVector(2, 1)


def test_normalize_setmag_limit():
    v = PCVector(3, 4)
    v.normalize()
    assert pytest.approx(v.mag(), rel=1e-7) == 1.0
    v.set_mag(10)
    assert pytest.approx(v.mag(), rel=1e-7) == 10.0
    v.limit(5)
    assert pytest.approx(v.mag(), rel=1e-7) == 5.0


def test_dot_and_heading():
    a = PCVector(1, 0)
    b = PCVector(0, 1)
    assert a.dot(b) == 0
    assert a.heading() == 0
    assert math.isclose(b.heading(), math.pi / 2)


def test_rotate_and_from_angle():
    v = PCVector(1, 0)
    v.rotate(math.pi / 2)
    assert pytest.approx(v.x, rel=1e-7) == 0.0
    assert pytest.approx(v.y, rel=1e-7) == 1.0
    u = PCVector.from_angle(math.pi / 4, math.sqrt(2))
    assert pytest.approx(u.x, rel=1e-7) == 1.0
    assert pytest.approx(u.y, rel=1e-7) == 1.0


def test_lerp_and_distance():
    a = PCVector(0, 0)
    b = PCVector(10, 0)
    a.lerp(b, 0.5)
    assert a == PCVector(5, 0)
    assert a.distance(PCVector(5, 0)) == 0


def test_tuple_and_sequence_inputs():
    v = PCVector(1, 2)
    v.add((1, 1))
    assert v == PCVector(2, 3)
    v.sub([1, 1])
    assert v == PCVector(1, 2)
