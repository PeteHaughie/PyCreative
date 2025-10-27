import types

import pycreative


def make_engine_stub(delegate=None):
    """Return a minimal engine-like object with an `api.get` method.

    `delegate` if provided should be a callable returned by api.get('blend_mode').
    """
    class ApiStub:
        def __init__(self, fn):
            self._fn = fn

        def get(self, name):
            if name == 'blend_mode':
                return self._fn
            return None

    eng = types.SimpleNamespace()
    eng.api = ApiStub(delegate)
    # other code expects attributes like `blend_mode` to be writable
    return eng


def test_pycreative_graphics_blend_mode_sets_engine_attribute(tmp_path):
    eng = make_engine_stub()
    # ensure no pre-existing attribute
    assert not hasattr(eng, 'blend_mode')
    pycreative.set_current_engine(eng)

    import pycreative.graphics as gfx

    gfx.blend_mode('ADD')

    assert hasattr(eng, 'blend_mode')
    assert eng.blend_mode == 'ADD'


def test_simple_sketch_api_delegates_and_sets_engine_state():
    called = []

    def delegate_fn(mode):
        called.append(mode)

    eng = make_engine_stub(delegate=delegate_fn)
    from core.engine.api.simple import SimpleSketchAPI

    api = SimpleSketchAPI(eng)
    # Should set engine.blend_mode and call the delegate
    api.blend_mode('MULTIPLY')

    assert getattr(eng, 'blend_mode', None) == 'MULTIPLY'
    assert called == ['MULTIPLY']


def test_blend_mode_records_command_into_graphics_buffer():
    from core.graphics.buffer import GraphicsBuffer
    eng = make_engine_stub()
    eng.graphics = GraphicsBuffer()
    # no delegate this time
    from core.engine.api.simple import SimpleSketchAPI

    api = SimpleSketchAPI(eng)
    api.blend_mode('SCREEN')

    # The graphics buffer should contain a recorded 'blend_mode' op
    cmds = getattr(eng.graphics, 'commands', [])
    assert any(c.get('op') == 'blend_mode' and c.get('args', {}).get('mode') == 'SCREEN' for c in cmds)
