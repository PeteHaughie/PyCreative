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
        # expose shape recording helpers so sketches can call begin_shape/vertex/end_shape
        if hasattr(_shape, 'begin_shape'):
            engine.api.register('begin_shape', lambda *a, **k: getattr(_shape, 'begin_shape')(engine, *a, **k))
        if hasattr(_shape, 'vertex'):
            engine.api.register('vertex', lambda *a, **k: getattr(_shape, 'vertex')(engine, *a, **k))
        if hasattr(_shape, 'end_shape'):
            engine.api.register('end_shape', lambda *a, **k: getattr(_shape, 'end_shape')(engine, *a, **k))
    except Exception:
        # best-effort only
        pass


def register_random_and_noise(engine: Any):
    try:
        from core.random import (
            random as _rand,
        )
        from core.random import (
            random_gaussian as _rand_gauss,
        )
        from core.random import (
            random_seed as _rand_seed,
        )
        from core.random import (
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
            from core.random import noise as _noise
            from core.random import noise_detail as _noise_detail
            from core.random import noise_seed as _noise_seed
            engine.api.register('noise', lambda *a, **k: _noise(engine, *a, **k))
            engine.api.register('noise_seed', lambda *a, **k: _noise_seed(engine, *a, **k))
            engine.api.register('noise_detail', lambda *a, **k: _noise_detail(engine, *a, **k))
        except Exception:
            pass
    except Exception:
        pass


def register_math(engine: Any):
    """Expose the small core.math helpers via the engine API so sketches
    can access them as `self.sin`, `self.cos`, `self.radians`, etc.
    """
    try:
        import core.math as _m
        # Register a small subset commonly used in sketches
        for name in ('sin', 'cos', 'tan', 'radians', 'degrees', 'sqrt', 'pow', 'abs_', 'floor', 'ceil'):
            if hasattr(_m, name):
                # Normalize names: core.math uses names like abs_ and map_
                target_name = name.rstrip('_')
                engine.api.register(target_name, lambda *a, _n=name, **k: getattr(_m, _n)(*a, **k))
    except Exception:
        pass


def register_state_apis(engine: Any):
    """Register simple color and stroke related APIs on the engine.

    These functions mutate engine state (fill_color, stroke_color,
    stroke_weight) and record corresponding graphics commands so sketches
    that call `fill()`, `stroke()`, etc continue to work in headless
    mode.
    """
    try:
        def _rec_fill(rgba):
            engine.fill_color = tuple(int(x) for x in rgba)
            return engine.graphics.record('fill', color=engine.fill_color, fill_alpha=getattr(engine, 'fill_alpha', None))

        def _rec_stroke(rgba):
            engine.stroke_color = tuple(int(x) for x in rgba)
            return engine.graphics.record('stroke', color=engine.stroke_color, stroke_alpha=getattr(engine, 'stroke_alpha', None))

        def _rec_no_fill():
            engine.fill_color = None
            try:
                return engine.graphics.record('no_fill')
            except Exception:
                return None

        def _rec_no_stroke():
            engine.stroke_color = None
            try:
                return engine.graphics.record('no_stroke')
            except Exception:
                return None

        def _rec_stroke_weight(w):
            engine.stroke_weight = int(w)
            return engine.graphics.record('stroke_weight', weight=int(w))

        def _rec_stroke_cap(cap):
            try:
                engine.stroke_cap = cap
            except Exception:
                pass
            try:
                return engine.graphics.record('stroke_cap', cap=cap)
            except Exception:
                return None

        def _rec_stroke_join(join):
            try:
                engine.stroke_join = join
            except Exception:
                pass
            try:
                return engine.graphics.record('stroke_join', join=join)
            except Exception:
                return None

        try:
            engine.api.register('fill', _rec_fill)
            engine.api.register('stroke', _rec_stroke)
            engine.api.register('stroke_weight', _rec_stroke_weight)
            # register cap/join recorders so sketches calling stroke_cap()/stroke_join()
            # during setup record the current state into the graphics buffer.
            try:
                engine.api.register('stroke_cap', _rec_stroke_cap)
                engine.api.register('stroke_join', _rec_stroke_join)
            except Exception:
                pass
            try:
                engine.api.register('no_fill', lambda *a, **k: _rec_no_fill())
                engine.api.register('no_stroke', lambda *a, **k: _rec_no_stroke())
            except Exception:
                pass
        except Exception:
            pass
    except Exception:
        # Best-effort only
        pass
