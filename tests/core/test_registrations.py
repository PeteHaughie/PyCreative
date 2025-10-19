import pytest

from core.engine.impl import Engine


def test_registers_shape_and_random_apis():
    eng = Engine(headless=True)
    # Commonly-registered APIs should be present in the API registry
    for name in ('rect', 'line', 'point', 'random', 'noise'):
        # registry.get returns a callable or raises
        fn = eng.api.get(name)
        assert callable(fn)


def test_state_apis_modify_engine_and_record():
    eng = Engine(headless=True)
    # fill should update engine.fill_color and record a command
    eng.api.get('fill')((123, 45, 6))
    assert eng.fill_color == (123, 45, 6)
    assert any(c.get('op') == 'fill' for c in eng.graphics.commands)

    # stroke weight
    eng.api.get('stroke_weight')(5)
    assert eng.stroke_weight == 5
    assert any(c.get('op') == 'stroke_weight' for c in eng.graphics.commands)
