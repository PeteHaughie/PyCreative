from core.engine.impl import Engine


def test_class_sketch_vertex_integration():
    class Sketch:
        def setup(self):
            # ensure instance has bound vertex via bindings
            assert hasattr(self, 'vertex') and callable(getattr(self, 'vertex'))
            self.begin_shape('POINTS')
            self.vertex(1, 2)
            self.end_shape()

        def draw(self):
            pass

    eng = Engine(sketch_module=Sketch(), headless=True)
    eng.run_frames(1)
    shapes = [c for c in eng.graphics.commands if c.get('op') in ('shape', 'invalid_shape')]
    assert shapes
