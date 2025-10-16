"""Small helpers to keep Engine.__init__ lean: register shape and random APIs.

This module centralizes third-party or optional API registrations so the
main Engine implementation stays compact and easier to review.
"""
from typing import Any


def register_shape_apis(engine: Any):
    # Import the shape module and look up functions by name at runtime.
    # This avoids mypy/static-import complaints when optional helpers
    # (like `ellipse`) are not present in the module.
    try:
        import core.shape as _shape
        if hasattr(_shape, 'rect'):
            engine.api.register('rect', lambda *a, **k: getattr(_shape, 'rect')(engine, *a, **k))
        if hasattr(_shape, 'line'):
            engine.api.register('line', lambda *a, **k: getattr(_shape, 'line')(engine, *a, **k))
        if hasattr(_shape, 'point'):
            engine.api.register('point', lambda *a, **k: getattr(_shape, 'point')(engine, *a, **k))

        # optional helpers
        if hasattr(_shape, 'circle'):
            engine.api.register('circle', lambda *a, **k: getattr(_shape, 'circle')(engine, *a, **k))
        if hasattr(_shape, 'ellipse'):
            engine.api.register('ellipse', lambda *a, **k: getattr(_shape, 'ellipse')(engine, *a, **k))
    except Exception:
        # best-effort only
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
