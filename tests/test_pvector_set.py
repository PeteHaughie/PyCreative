import pytest

from pycreative.vector import PVector


def test_set_with_numbers_and_chaining():
    v = PVector(1, 2)
    ret = v.set(3, 4)
    assert v.x == pytest.approx(3.0)
    assert v.y == pytest.approx(4.0)
    # set should return self for chaining
    assert ret is v


def test_set_with_pvector_and_iterable():
    v = PVector(0, 0)
    other = PVector(5.5, -2.25)
    v.set(other)
    assert v.x == pytest.approx(5.5)
    assert v.y == pytest.approx(-2.25)

    v.set([7, 8])
    assert v.x == pytest.approx(7.0)
    assert v.y == pytest.approx(8.0)


def test_set_invalid_calls():
    v = PVector(0, 0)
    with pytest.raises(TypeError):
        v.set([1])  # too-short iterable
    with pytest.raises(TypeError):
        v.set(1)  # single numeric arg without iterable
