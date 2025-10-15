import pytest

from core.engine.impl import Engine
from core.engine.api import SimpleSketchAPI


def test_background_rgb_and_gray_recorded():
    eng = Engine(headless=True)
    api = SimpleSketchAPI(eng)
    api.background(51)
    api.background(10, 20, 30)
    cmds = eng.graphics.commands
    assert any(c['op'] == 'background' and c['args']['r'] == 51 for c in cmds)
    assert any(c['op'] == 'background' and c['args']['r'] == 10 and c['args']['g'] == 20 and c['args']['b'] == 30 for c in cmds)


def test_background_alpha_disallowed_on_main_engine():
    eng = Engine(headless=True)
    api = SimpleSketchAPI(eng)
    with pytest.raises(TypeError):
        api.background(100, 0.5)


def test_background_alpha_allowed_on_offscreen_graphics():
    eng = Engine(headless=True)
    # mark as offscreen graphics (PCGraphics-like) to allow alpha
    eng._is_offscreen_graphics = True
    api = SimpleSketchAPI(eng)
    api.background(10, 20, 30, 0.25)
    cmds = eng.graphics.commands
    assert any(c['op'] == 'background' and c['args'].get('a') is not None for c in cmds)
