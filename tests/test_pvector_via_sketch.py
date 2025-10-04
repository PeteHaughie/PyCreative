from pycreative.app import Sketch
from pycreative.vector import PVector


def test_sketch_pvector_factory():
    s = Sketch()
    v = s.pvector(3, 4)
    assert isinstance(v, PVector)
    assert v.x == 3 and v.y == 4
