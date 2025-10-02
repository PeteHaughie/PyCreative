def test_map_basic():
    from pycreative.app import Sketch

    s = Sketch()
    # map 0.5 from range 0..1 to 0..10 -> 5
    assert s.map(0.5, 0, 1, 0, 10) == 5.0


def test_map_inverse():
    from pycreative.app import Sketch

    s = Sketch()
    # mapping back should round-trip
    x = 3.2
    y = s.map(x, 0, 10, 100, 200)
    x2 = s.map(y, 100, 200, 0, 10)
    assert abs(x - x2) < 1e-9


def test_map_divide_by_zero():
    from pycreative.app import Sketch

    s = Sketch()
    # start1 == stop1 -> avoid crash, return start2
    assert s.map(1, 0, 0, 10, 20) == 10.0
