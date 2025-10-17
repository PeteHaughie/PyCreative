from core.util.loader import load_module_from_path
from core.engine.impl import Engine


def test_attract_does_not_mutate_position():
    mod = load_module_from_path('examples/Nature of Code/chapter02/Example_2_06_Attraction/Example_2_06_Attraction.py')
    eng = Engine(sketch_module=mod, headless=True)
    eng.run_frames(1)
    sk = eng.sketch
    attr = sk.attractor
    mover = sk.mover
    # snapshot position
    before_x, before_y = attr.position.x, attr.position.y
    # call attract
    f = attr.attract(mover)
    # position should be unchanged
    assert abs(attr.position.x - before_x) < 1e-9
    assert abs(attr.position.y - before_y) < 1e-9
    # also ensure a force vector was returned
    assert hasattr(f, 'x') and hasattr(f, 'y')
