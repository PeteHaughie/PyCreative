def test_pvector_dist_instance_and_classstyle():
    from pycreative.vector import PVector
    import math

    v1 = PVector(10, 20)
    v2 = PVector(60, 80)

    # expected distance between (10,20) and (60,80)
    expected = math.hypot(50, 60)

    # instance method
    d1 = v1.dist(v2)
    assert abs(d1 - expected) < 1e-9

    # class-style/unbound call (PVector.dist(v1, v2)) should work too
    d2 = PVector.dist(v1, v2)
    assert abs(d2 - expected) < 1e-9

    # iterable input
    d3 = v1.dist((60, 80))
    assert abs(d3 - expected) < 1e-9
