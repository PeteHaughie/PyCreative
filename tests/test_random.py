def test_random_seed_reproducible():
    from pycreative.app import Sketch

    s = Sketch()
    s.random_seed(42)
    a = s.random()
    s.random_seed(42)
    b = s.random()
    assert a == b


def test_random_ranges():
    from pycreative.app import Sketch

    s = Sketch()
    # default 0..1
    v = s.random()
    assert 0.0 <= v < 1.0

    h = s.random(10)
    assert 0.0 <= h < 10.0

    r = s.random(5, 6)
    assert 5.0 <= r < 6.0
