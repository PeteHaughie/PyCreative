import pytest

from core.engine import Engine
from core.engine.api import SimpleSketchAPI


def test_fill_alpha_accepts_0_to_1_and_0_to_255_and_clamps():
    eng = Engine(headless=True)
    eng._is_offscreen_graphics = True
    api = SimpleSketchAPI(eng)

    api.fill(10, 255)  # 255 -> 1.0
    assert pytest.approx(eng.fill_alpha, rel=1e-6) == 1.0

    api.fill(10, 128)  # 128 -> 128/255
    assert pytest.approx(eng.fill_alpha, rel=1e-6) == 128.0 / 255.0

    api.fill(10, 0.5)  # already 0..1
    assert pytest.approx(eng.fill_alpha, rel=1e-6) == 0.5

    api.fill(10, -10)  # clamp to 0
    assert pytest.approx(eng.fill_alpha, rel=1e-6) == 0.0

    api.fill(10, 9999)  # clamp to 1
    assert pytest.approx(eng.fill_alpha, rel=1e-6) == 1.0


def test_fill_alpha_non_numeric_raises():
    eng = Engine(headless=True)
    eng._is_offscreen_graphics = True
    api = SimpleSketchAPI(eng)

    with pytest.raises(TypeError):
        api.fill(10, 'not-a-number')


def test_fill_alpha_enforced_offscreen_only():
    eng = Engine(headless=True)
    api = SimpleSketchAPI(eng)

    # Alpha is allowed on main engine now; ensure it's normalized
    api.fill(10, 128)
    assert pytest.approx(eng.fill_alpha, rel=1e-6) == 128.0 / 255.0
