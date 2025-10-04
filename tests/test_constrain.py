from pycreative.app import Sketch


def test_constrain_within_range():
    s = Sketch()
    assert s.constrain(5, 0, 10) == 5


def test_constrain_below_min():
    s = Sketch()
    assert s.constrain(-1, 0, 10) == 0


def test_constrain_above_max():
    s = Sketch()
    assert s.constrain(11, 0, 10) == 10


def test_constrain_float_and_swap_min_max():
    s = Sketch()
    # min > max should swap
    assert s.constrain(2.5, 5.0, 1.0) == 2.5
    assert s.constrain(0.5, 5.0, 1.0) == 1.0


def test_constrain_preserves_int_type_when_possible():
    s = Sketch()
    assert isinstance(s.constrain(3, 0, 5), int)
    assert isinstance(s.constrain(3.2, 0, 5), float)
