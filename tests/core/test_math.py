from core import math as cm


def test_constrain_and_lerp_and_dist():
    assert cm.constrain(5, 0, 10) == 5
    assert cm.constrain(-1, 0, 10) == 0
    assert cm.lerp(0, 10, 0.5) == 5
    assert round(cm.dist(0, 0, 3, 4), 6) == 5


def test_map_and_mag_and_sq():
    v = cm.map_(5, 0, 10, 0, 100)
    assert round(v, 6) == 50
    assert round(cm.mag(3, 4), 6) == 5
    assert cm.sq(3) == 9


def test_pcvector():
    p = cm.PCVector(3, 4)
    assert round(p.mag(), 6) == 5
    p.add(cm.PCVector(1, 2))
    assert p.to_tuple() == (4.0, 6.0)
