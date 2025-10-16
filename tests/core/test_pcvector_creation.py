import pytest
from core.math import PCVector


def test_creation_and_set_tuple():
    v = PCVector(3, 4)
    assert v.to_tuple() == (3.0, 4.0)
    v.set(1, 2)
    assert v.to_tuple() == (1.0, 2.0)


def test_mag_copy_and_equality():
    v = PCVector(3, 4)
    assert pytest.approx(v.mag(), rel=1e-7) == 5.0
    c = v.copy()
    assert c == v
    c.x = 0
    assert c != v
