"""Small helpers to keep Engine.__init__ lean: register shape and random APIs.

This module centralizes third-party or optional API registrations so the
main Engine implementation stays compact and easier to review.
"""
from typing import Any


def register_shape_apis(engine: Any):
    try:
        from core.shape import rect as _rect, line as _line, point as _point
        engine.api.register('rect', lambda *a, **k: _rect(engine, *a, **k))
        engine.api.register('line', lambda *a, **k: _line(engine, *a, **k))
        engine.api.register('point', lambda *a, **k: _point(engine, *a, **k))
    except Exception:
        # best-effort only
        pass

    # optional helpers
    try:
        from core.shape import circle as _circle
        engine.api.register('circle', lambda *a, **k: _circle(engine, *a, **k))
    except Exception:
        pass
    try:
        from core.shape import ellipse as _ellipse
        engine.api.register('ellipse', lambda *a, **k: _ellipse(engine, *a, **k))
    except Exception:
        pass


def register_random_and_noise(engine: Any):
    try:
        from core.random import (
            random as _rand,
            random_seed as _rand_seed,
            random_gaussian as _rand_gauss,
            uniform as _rand_uniform,
        )
        engine.api.register('random', lambda *a, **k: _rand(engine, *a, **k))
        engine.api.register('random_seed', lambda *a, **k: _rand_seed(engine, *a, **k))
        try:
            engine.api.register('random_gaussian', lambda *a, **k: _rand_gauss(engine, *a, **k))
        except Exception:
            pass
        try:
            engine.api.register('uniform', lambda *a, **k: _rand_uniform(engine, *a, **k))
        except Exception:
            pass
        # noise family
        try:
            from core.random import noise as _noise, noise_seed as _noise_seed, noise_detail as _noise_detail
            engine.api.register('noise', lambda *a, **k: _noise(engine, *a, **k))
            engine.api.register('noise_seed', lambda *a, **k: _noise_seed(engine, *a, **k))
            engine.api.register('noise_detail', lambda *a, **k: _noise_detail(engine, *a, **k))
        except Exception:
            pass
    except Exception:
        pass
