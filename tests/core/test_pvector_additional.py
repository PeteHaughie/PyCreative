import pytest
import math
from core.math import PCVector


def test_set_and_negation():
    v = PCVector(0, 0)
    v.set(3, 4)
    assert v == PCVector(3, 4)
    # negation
    n = -v
    assert n == PCVector(-3, -4)


def test_componentwise_mult_div():
    a = PCVector(2, 3)
    b = PCVector(4, 5)
    # component-wise multiply
    a.mult(b)
    assert a == PCVector(8, 15)
    # component-wise divide
    a.div(PCVector(2, 3))
    assert a == PCVector(4, 5)


def test_division_by_zero_scalar_and_vector():
    v = PCVector(1, 2)
    with pytest.raises(ZeroDivisionError):
        v.div(0)
    with pytest.raises(ZeroDivisionError):
        v.div(PCVector(0, 1))
    with pytest.raises(ZeroDivisionError):
        v.div(PCVector(1, 0))


def test_unpacked_other_errors():
    v = PCVector(1, 2)
    # calling add with a single numeric arg without y should raise
    with pytest.raises(TypeError):
        v.add(1)
    # passing a wrong-length sequence should raise ValueError
    with pytest.raises(ValueError):
        v.add((1, 2, 3))
