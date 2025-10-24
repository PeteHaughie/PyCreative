"""Engine API registrations moved into the api package.

This module contains helpers that register shape, random, and math
functions onto an Engine's APIRegistry. It was moved from
``core.engine.registrations`` to keep engine internals organized.
"""
from typing import Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


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
            # optional vectorized field generator
            _noise_field: Optional[Callable[..., Any]] = None
            try:
                # noise_field is implemented in core.random.ops; try importing
                # directly to avoid relying on package re-exports.
                from core.random.ops import noise_field as _noise_field_impl
                _noise_field = _noise_field_impl
            except Exception:
                _noise_field = None
            engine.api.register('noise', lambda *a, **k: _noise(engine, *a, **k))
            engine.api.register('noise_seed', lambda *a, **k: _noise_seed(engine, *a, **k))
            engine.api.register('noise_detail', lambda *a, **k: _noise_detail(engine, *a, **k))
            if _noise_field is not None:
                engine.api.register('noise_field', lambda *a, **k: _noise_field(engine, *a, **k))
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


def register_image_apis(engine: Any):
    """Register image loading APIs on the engine (load_image/request_image/create_image)."""
    try:
        import os

        from core.image import load_image as _load, request_image as _req, create_image as _create

        def _resolve(pth: str) -> str:
            try:
                if os.path.isabs(pth):
                    return pth
            except Exception:
                pass

            # determine sketch dir from engine._sketch_module or engine.sketch
            sketch_dir = None
            try:
                smod = getattr(engine, '_sketch_module', None)
                if smod is not None:
                    sf = getattr(smod, '__file__', None)
                    if sf:
                        sketch_dir = os.path.dirname(os.path.abspath(sf))
            except Exception:
                sketch_dir = None

            if sketch_dir is None:
                try:
                    s = getattr(engine, 'sketch', None)
                    if s is not None:
                        sf = getattr(s, '__file__', None)
                        if sf:
                            sketch_dir = os.path.dirname(os.path.abspath(sf))
                except Exception:
                    sketch_dir = None

            if sketch_dir is None:
                return pth

            # prefer data/ subfolder
            data_path = os.path.join(sketch_dir, 'data', pth)
            if os.path.exists(data_path):
                return data_path
            # fallback to sketch dir
            sketch_path = os.path.join(sketch_dir, pth)
            if os.path.exists(sketch_path):
                return sketch_path
            # last resort: return original path
            return pth

        def _load_wrapper(path: str, extension: Any = None):
            p = _resolve(path)
            # Verbose/debug: report the resolved path so CLI runs can show where
            # images were loaded from. Use engine._verbose when available so the
            # CLI's --verbose flag surfaces this information.
            try:
                if getattr(engine, '_verbose', False):
                    try:
                        # print directly to stdout so CLI --verbose users see it
                        print(f"load_image: resolved '{path}' -> '{p}'")
                    except Exception:
                        pass
                else:
                    # Lower-volume logging for normal runs
                    try:
                        if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                            logger.debug("load_image resolved '%s' -> '%s'", path, p)
                    except Exception:
                        pass
            except Exception:
                pass
            return _load(p, extension)

        def _request_wrapper(path: str, extension: Any = None):
            p = _resolve(path)
            try:
                if getattr(engine, '_verbose', False):
                    try:
                        print(f"request_image: resolved '{path}' -> '{p}'")
                    except Exception:
                        pass
                else:
                    try:
                        if os.getenv('PYCREATIVE_DEBUG_LIFECYCLE', '') == '1':
                            logger.debug("request_image resolved '%s' -> '%s'", path, p)
                    except Exception:
                        pass
            except Exception:
                pass
            return _req(p, extension)

        engine.api.register('load_image', lambda *a, **k: _load_wrapper(*a, **k))
        engine.api.register('request_image', lambda *a, **k: _request_wrapper(*a, **k))
        engine.api.register('create_image', lambda *a, **k: _create(*a, **k))
    except Exception:
        # best-effort only
        pass
