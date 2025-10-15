from core.engine import Engine
from core.engine.api import SimpleSketchAPI


def test_math_helpers_exposed():
    eng = Engine(headless=True)
    api = SimpleSketchAPI(eng)
    # smoke-test math helpers that have API docs
    for name in ('lerp', 'map', 'dist', 'sqrt', 'pow'):
        assert hasattr(api, name), f"API missing math helper: {name}"

    # Functional checks for documented helpers
    assert api.lerp(0, 10, 0.5) == 5.0
    assert api.map(25, 0, 100, 0, 200) == 50.0
    assert api.dist(0, 0, 3, 4) == 5.0
    assert api.sqrt(9) == 3.0
    assert api.pow(2, 3) == 8


def test_pcvector_factory():
    eng = Engine(headless=True)
    api = SimpleSketchAPI(eng)
    v = api.pcvector(2, 3)
    assert v.x == 2
    assert v.y == 3
    # vector ops
    v2 = v.copy()
    v2.add((1, 1))
    assert v2.x == 3 and v2.y == 4
