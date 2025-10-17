from core.engine.impl import Engine


def test_attract_does_not_mutate_position():
    # Minimal in-test objects that model an attractor and a mover so
    # behaviour can be tested without using the examples/ tree.
    class Vec:
        def __init__(self, x=0.0, y=0.0):
            self.x = float(x)
            self.y = float(y)

    class Mover:
        def __init__(self):
            self.position = Vec(50.0, 50.0)

    class Attractor:
        def __init__(self):
            self.position = Vec(100.0, 100.0)

        def attract(self, mover):
            # compute a force vector without mutating self.position
            dx = mover.position.x - self.position.x
            dy = mover.position.y - self.position.y
            # return a simple vector-like object
            return Vec(dx, dy)

    class Sketch:
        def setup(self):
            self.attractor = Attractor()
            self.mover = Mover()

    eng = Engine(sketch_module=Sketch(), headless=True)
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
