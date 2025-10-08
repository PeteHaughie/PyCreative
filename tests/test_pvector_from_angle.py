def test_from_angle_and_fromAngle_mutation_and_alias():
    from pycreative.vector import PVector
    import math

    a = 0.5
    v_new = PVector.from_angle(a)
    assert isinstance(v_new, PVector)
    # should be unit-length (approximately)
    mag = (v_new.x ** 2 + v_new.y ** 2) ** 0.5
    assert abs(mag - 1.0) < 1e-6

    # target mutation
    target = PVector(0, 0)
    v_target = PVector.from_angle(a, target)
    assert v_target is target
    assert abs(target.x - math.cos(a)) < 1e-12
    assert abs(target.y - math.sin(a)) < 1e-12

    # API uses snake_case only; ensure alias isn't required.
