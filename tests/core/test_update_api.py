import pytest

from core.engine.impl import Engine


class SketchWithUpdate:
    def __init__(self):
        self.calls = []

    def setup(self, this):
        # called once
        self.calls.append(('setup', None))

    def update(self, this):
        # record that update ran; also mutate state to be observed in draw
        self.calls.append(('update', None))
        # attach a value to verify ordering
        self.last_updated = len(self.calls)

    def draw(self, this):
        # record draw and assert update happened at least once before draw
        self.calls.append(('draw', None))
        # store the observed last_updated value onto the draw for assertions
        try:
            self.draw_observed = getattr(self, 'last_updated', None)
        except Exception:
            self.draw_observed = None


def test_update_runs_before_draw_multiple_frames():
    sketch = SketchWithUpdate()
    eng = Engine(sketch_module=sketch, headless=True)

    # run two frames; update should run once per frame before draw
    eng.run_frames(2, ignore_no_loop=True)

    # Expect: setup once, (update, draw) twice
    names = [n for (n, _) in sketch.calls]
    assert names.count('setup') == 1
    # total updates and draws should both be 2
    assert names.count('update') == 2
    assert names.count('draw') == 2

    # Verify ordering: for each frame, update appears before the corresponding draw
    # We'll scan the sequence to ensure for each draw the previous event was an update
    seq = names
    draws_indices = [i for i, x in enumerate(seq) if x == 'draw']
    for idx in draws_indices:
        assert idx > 0
        assert seq[idx - 1] == 'update'

    # The draw should have observed the last_updated value set during update
    assert sketch.draw_observed is not None
    # last_updated should be <= total calls length
    assert sketch.draw_observed <= len(sketch.calls)
