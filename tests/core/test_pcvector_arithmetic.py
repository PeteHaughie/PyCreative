import pytest
from core.math import PCVector


def test_add_and_sub_overloads():
    a = PCVector(1, 2)
    b = PCVector(3, 4)
    a.add(b)
    assert a == PCVector(4, 6)
    a.add((1, 1))
    assert a == PCVector(5, 7)
    a.add([1, 1])
    assert a == PCVector(6, 8)
    a.add(1, 1)
    assert a == PCVector(7, 9)

    a = PCVector(5, 5)
    a.sub(1, 2)
    assert a == PCVector(4, 3)
    a.sub((1, 1))
    assert a == PCVector(3, 2)
    a.sub(PCVector(1, 1))
    assert a == PCVector(2, 1)


def test_mult_div_scalar_and_vector_and_zero_division():
    v = PCVector(2, 3)
    v.mult(2)
    assert v == PCVector(4, 6)
    v.div(2)
    assert v == PCVector(2, 3)
    v.mult(PCVector(2, 2))
    assert v == PCVector(4, 6)
    v.div(PCVector(2, 2))
    assert v == PCVector(2, 3)

    v = PCVector(1, 2)
    with pytest.raises(ZeroDivisionError):
        v.div(0)
    with pytest.raises(ZeroDivisionError):
        v.div(PCVector(0, 1))


def test_operator_overloads_and_unary():
    v = PCVector(1, 2)
    assert v + PCVector(1, 1) == PCVector(2, 3)
    assert v - PCVector(1, 1) == PCVector(0, 1)
    assert v * 2 == PCVector(2, 4)
    assert v / 1 == PCVector(1, 2)
    assert -v == PCVector(-1, -2)
