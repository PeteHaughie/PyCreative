import pytest

from core.engine.impl import Engine


class DummySketch:
    def __init__(self):
        self.setup_called = False
        self.draw_called = 0

    def setup(self):
        self.setup_called = True

    def draw(self):
        self.draw_called += 1


def test_headless_run_frames_executes_setup_and_draw_once():
    s = DummySketch()
    eng = Engine(sketch_module=s, headless=True)
    # run a single frame; setup should be called once and draw once
    eng.run_frames(1)
    assert s.setup_called is True
    assert s.draw_called >= 1
