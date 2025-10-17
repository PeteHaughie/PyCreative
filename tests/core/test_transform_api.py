import types

from core.engine import Engine


def _make_module_with_setup(fn):
    m = types.SimpleNamespace()
    m.setup = fn
    return m


def test_translate_records_command():
    """Calling this.translate(x,y) in setup should record a 'translate' op."""

    def setup(this):
        # spec: this.translate should exist and record a translate op
        this.translate(10, 20)

    engine = Engine(sketch_module=_make_module_with_setup(setup), headless=True)
    engine.run_frames(1)

    ops = [c['op'] for c in engine.graphics.commands]
    assert 'translate' in ops


def test_rotate_records_command():
    def setup(this):
        this.rotate(1.234)

    engine = Engine(sketch_module=_make_module_with_setup(setup), headless=True)
    engine.run_frames(1)

    ops = [c['op'] for c in engine.graphics.commands]
    assert 'rotate' in ops


def test_scale_records_command():
    def setup(this):
        this.scale(2.0)

    engine = Engine(sketch_module=_make_module_with_setup(setup), headless=True)
    engine.run_frames(1)

    ops = [c['op'] for c in engine.graphics.commands]
    assert 'scale' in ops


def test_push_pop_matrix_records_commands():
    def setup(this):
        this.push_matrix()
        this.pop_matrix()

    engine = Engine(sketch_module=_make_module_with_setup(setup), headless=True)
    engine.run_frames(1)

    ops = [c['op'] for c in engine.graphics.commands]
    # Some implementations may record these as 'push_matrix'/'pop_matrix'
    # or as canvas-style 'save'/'restore' ops. Accept either form.
    assert any(x in ops for x in ('push_matrix', 'pushMatrix', 'save'))
    assert any(x in ops for x in ('pop_matrix', 'popMatrix', 'restore'))


def test_shear_records_command():
    def setup(this):
        sx = getattr(this, 'shear_x', None)
        sy = getattr(this, 'shear_y', None)
        assert callable(sx), 'this.shear_x must be implemented'
        assert callable(sy), 'this.shear_y must be implemented'
        sx(0.5)
        sy(0.25)

    engine = Engine(sketch_module=_make_module_with_setup(setup), headless=True)
    engine.run_frames(1)

    ops = [c['op'] for c in engine.graphics.commands]
    assert 'shear_x' in ops or 'shearX' in ops
    assert 'shear_y' in ops or 'shearY' in ops


def test_reset_and_apply_matrix_record_commands():
    def setup(this):
        # reset matrix should record a reset op
        rm = getattr(this, 'reset_matrix', None)
        am = getattr(this, 'apply_matrix', None)
        assert callable(rm), 'this.reset_matrix must be implemented'
        assert callable(am), 'this.apply_matrix must be implemented'
        rm()
        # apply matrix via 16 numbers
        am(
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1,
        )

    engine = Engine(sketch_module=_make_module_with_setup(setup), headless=True)
    engine.run_frames(1)

    ops = [c['op'] for c in engine.graphics.commands]
    assert 'reset_matrix' in ops or 'resetMatrix' in ops
    assert 'apply_matrix' in ops or 'applyMatrix' in ops
