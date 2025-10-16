import math
import pytest
from core.math import PCVector, lerp


def test_normalize_setmag_limit_and_lerp():
    v = PCVector(3, 4)
    v.normalize()
    assert pytest.approx(v.mag(), rel=1e-7) == 1.0
    v.set_mag(10)
    assert pytest.approx(v.mag(), rel=1e-7) == 10.0
    v.limit(5)
    assert pytest.approx(v.mag(), rel=1e-7) == 5.0

    a = PCVector(0, 0)
    b = PCVector(10, 0)
    a.lerp(b, 0.5)
    assert a == PCVector(5, 0)


def test_dot_heading_rotate_from_angle_and_distance():
    a = PCVector(1, 0)
    b = PCVector(0, 1)
    assert a.dot(b) == 0
    assert a.heading() == 0
    v = PCVector(1, 0)
    v.rotate(math.pi / 2)
    assert pytest.approx(v.x, rel=1e-7) == 0.0
    assert pytest.approx(v.y, rel=1e-7) == 1.0
    u = PCVector.from_angle(math.pi / 4, math.sqrt(2))
    assert pytest.approx(u.x, rel=1e-7) == 1.0
    assert pytest.approx(u.y, rel=1e-7) == 1.0

    a = PCVector(0, 0)
    assert a.distance(PCVector(5, 0)) == 5


def test_unpacking_error_paths():
    v = PCVector(1, 2)
    with pytest.raises(TypeError):
        v.add(1)
    with pytest.raises(ValueError):
        v.add((1, 2, 3))
