import pytest

from core.engine import Engine
from core.engine.api import SimpleSketchAPI


def test_fill_overloads_and_alpha():
    eng = Engine(headless=True)
    api = SimpleSketchAPI(eng)

    # gray
    api.fill(120)
    assert eng.fill_color == (120, 120, 120)
    assert getattr(eng, 'fill_alpha', None) is None

    # rgb
    api.fill(10, 20, 30)
    assert eng.fill_color == (10, 20, 30)
    assert getattr(eng, 'fill_alpha', None) is None

    # tuple
    api.fill((200, 201, 202))
    assert eng.fill_color == (200, 201, 202)

    # alpha not allowed on main engine
    with pytest.raises(TypeError):
        api.fill(10, 0.5)

    # alpha allowed if marked offscreen
    eng2 = Engine(headless=True)
    eng2._is_offscreen_graphics = True
    api2 = SimpleSketchAPI(eng2)
    api2.fill(10, 20, 30, 0.4)
    assert eng2.fill_color == (10, 20, 30)
    assert pytest.approx(eng2.fill_alpha, 0.0001) == 0.4


def test_stroke_overloads_and_alpha():
    eng = Engine(headless=True)
    api = SimpleSketchAPI(eng)

    api.stroke(180)
    assert eng.stroke_color == (180, 180, 180)
    assert getattr(eng, 'stroke_alpha', None) is None

    api.stroke(5, 6, 7)
    assert eng.stroke_color == (5, 6, 7)

    with pytest.raises(TypeError):
        api.stroke(10, 0.2)

    eng2 = Engine(headless=True)
    eng2._is_offscreen_graphics = True
    api2 = SimpleSketchAPI(eng2)
    api2.stroke(1, 2, 3, 0.75)
    assert eng2.stroke_color == (1, 2, 3)
    assert pytest.approx(eng2.stroke_alpha, 0.0001) == 0.75
