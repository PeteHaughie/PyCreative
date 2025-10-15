from core.engine import Engine


def test_class_sketch_receives_dynamic_width_height():
    eng = Engine(headless=True)

    class MySketch:
        def setup(self):
            # initially engine default is 200x200
            assert self.width == 200
            assert self.height == 200
            # change size in setup
            self.size(320, 240)

        def draw(self):
            # size should have updated
            assert self.width == 320
            assert self.height == 240

    eng.sketch = MySketch
    eng._normalize_sketch()
    # run one frame to invoke setup + draw
    eng.run_frames(1)
