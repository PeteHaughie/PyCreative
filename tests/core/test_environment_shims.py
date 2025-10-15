from core.engine import Engine
import pycreative


def test_width_height_shims_reflect_engine_size():
    eng = Engine(headless=True)
    eng._set_size(320, 240)
    pycreative.set_current_engine(eng)
    assert pycreative.width == 320
    assert pycreative.height == 240
