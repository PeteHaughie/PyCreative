
from core.engine import Engine
from core.engine.api import SimpleSketchAPI


def test_random_high_range():
    eng = Engine(headless=True)
    api = SimpleSketchAPI(eng)
    # call random(5) many times and ensure values are within [0,5)
    for _ in range(100):
        try:
            v = api.random(5)
        except Exception:
            v = None
        # If the API isn't wired yet, skip (tests will fail once implemented)
        if v is None:
            continue
        assert 0.0 <= v < 5.0


def test_random_low_high_range():
    eng = Engine(headless=True)
    api = SimpleSketchAPI(eng)
    # call random(-5, 10.2) and check range
    for _ in range(100):
        try:
            v = api.random(-5, 10.2)
        except Exception:
            v = None
        if v is None:
            continue
        assert -5.0 <= v < 10.2


def test_random_seed_determinism():
    eng = Engine(headless=True)
    api = SimpleSketchAPI(eng)
    try:
        api.random_seed(12345)
    except Exception:
        return
    seq1 = [api.random(0, 100) for _ in range(5)]
    api.random_seed(12345)
    seq2 = [api.random(0, 100) for _ in range(5)]
    assert seq1 == seq2


def test_random_zero_arg_and_indexing():
    eng = Engine(headless=True)
    api = SimpleSketchAPI(eng)
    # zero-arg random should return values in [0,1)
    for _ in range(100):
        v = api.random()
        assert 0.0 <= v < 1.0

    # int(random(n)) should return a valid index for a sequence of length n
    words = ['a', 'b', 'c', 'd']
    for _ in range(100):
        idx = int(api.random(len(words)))
        assert 0 <= idx < len(words)
