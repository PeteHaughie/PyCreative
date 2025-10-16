import types
from core.engine import Engine


def make_sketch_with_setup_bg():
    mod = types.SimpleNamespace()
    def setup(this):
        this.background(0, 255, 0)
    def draw(this):
        this.rect(10, 10, 100, 200)
    mod.setup = setup
    mod.draw = draw
    return mod


def make_sketch_without_setup_bg():
    mod = types.SimpleNamespace()
    def setup(this):
        # no background called
        this.fill(255, 0, 0)
    def draw(this):
        this.rect(10, 10, 100, 200)
    mod.setup = setup
    mod.draw = draw
    return mod


def test_headless_captures_setup_background_once():
    sketch = make_sketch_with_setup_bg()
    eng = Engine(sketch_module=sketch, headless=True)
    # run first frame in headless mode
    eng.run_frames(1)
    # After first run, engine should have captured setup background
    assert getattr(eng, '_setup_background', None) == (0, 255, 0)
    # The recorded commands for the first frame should include a background
    # as the first op (headless run inserts the setup background into cmds)
    cmds = eng.graphics.commands
    assert len(cmds) > 0
    first_ops = [c.get('op') for c in cmds]
    assert first_ops[0] == 'background'
    # Running a second frame should NOT re-insert the setup background
    eng.run_frames(1)
    cmds2 = eng.graphics.commands
    if len(cmds2) > 0:
        assert cmds2[0].get('op') != 'background'


def test_headless_no_default_background_when_not_set():
    sketch = make_sketch_without_setup_bg()
    eng = Engine(sketch_module=sketch, headless=True)
    eng.run_frames(2)
    # When the sketch did not call background() in setup, headless engine should
    # NOT insert a default background automatically. Recorded commands should
    # reflect only what the sketch emitted.
    cmds = eng.graphics.commands
    # The first op SHOULD NOT be 'background' (headless should not insert default)
    if len(cmds) > 0:
        assert cmds[0].get('op') != 'background'


def test_no_loop_respected_but_cli_override():
    # Sketch that calls no_loop in setup(), but we override via run_frames
    mod = types.SimpleNamespace()
    def setup(this):
        this.no_loop()
        this.background(10, 20, 30)
    def draw(this):
        this.rect(1, 1, 2, 2)
    mod.setup = setup
    mod.draw = draw

    eng = Engine(sketch_module=mod, headless=True)
    # run_frames with ignore_no_loop via run_frames API should still draw both frames
    eng.run_frames(2, ignore_no_loop=True)
    # After run_frames the frame_count should be 2
    assert eng.frame_count == 2
    # setup_background should be captured
    assert getattr(eng, '_setup_background', None) == (10, 20, 30)
