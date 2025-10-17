from core.engine.impl import Engine


def test_attractor_handle_drag_updates_position():
    # Minimal, in-test sketch that exposes an attractor with the
    # behaviour under test. This avoids depending on the examples/ tree.
    class Vec:
        def __init__(self, x=0.0, y=0.0):
            self.x = float(x)
            self.y = float(y)

    class Attractor:
        def __init__(self):
            self.position = Vec(100.0, 100.0)
            self.drag_offset = Vec(0.0, 0.0)
            self.dragging = False

        def handle_press(self, px, py):
            self.dragging = True

        def handle_drag(self, mx, my):
            if self.dragging:
                # Update position considering drag_offset
                self.position.x = float(mx) + float(self.drag_offset.x)
                self.position.y = float(my) + float(self.drag_offset.y)

    class Sketch:
        def setup(self):
            self.attractor = Attractor()

    eng = Engine(sketch_module=Sketch(), headless=True)
    eng.run_frames(1)
    sk = eng.sketch
    attr = getattr(sk, 'attractor')
    # sanity
    assert hasattr(attr, 'position')
    # simulate pressing and set drag offset
    attr.handle_press(attr.position.x, attr.position.y)
    assert attr.dragging is True
    attr.drag_offset.x = 5.0
    attr.drag_offset.y = -3.0
    # perform drag
    mx = attr.position.x + 10.0
    my = attr.position.y + 20.0
    # call handle_drag which should update attr.position
    old_x, old_y = attr.position.x, attr.position.y
    attr.handle_drag(mx, my)
    assert attr.position.x != old_x or attr.position.y != old_y
    # ensure the new position matches mx + drag_offset
    assert abs(attr.position.x - (mx + 5.0)) < 1e-6
    assert abs(attr.position.y - (my - 3.0)) < 1e-6
