"""Public shims for the pycreative API.

These small functions delegate to a currently configured Engine instance so
that sketches and examples can `from pycreative import size, background, rect`
without importing internal modules.

Keep this module tiny to avoid heavy import-time side-effects.
"""
from __future__ import annotations

from typing import Any, Optional

_current_engine: Optional[Any] = None

# NOTE: imports in this module are performed lazily to avoid import-time
# cycles during tests. Keep top-level state minimal.


def set_current_engine(engine: Any) -> None:
    """Set the active Engine instance used by top-level shims."""
    global _current_engine
    _current_engine = engine


def get_current_engine() -> Any:
    """Return the currently registered Engine or raise RuntimeError."""
    if _current_engine is None:
        raise RuntimeError('no current engine set; call set_current_engine(engine)')
    return _current_engine


def _get_engine():
    return get_current_engine()


# Explicit, minimal shims — no heuristics. Each shim directly delegates to
# the appropriate core package or engine method so the mapping is obvious
# and easy to maintain.


def size(w: int, h: int):
    eng = _get_engine()
    return eng._set_size(w, h)


def background(*args):
    eng = _get_engine()
    # Use the SimpleSketchAPI implementation which normalises HSB/RGB modes
    from core.engine.api import SimpleSketchAPI
    return SimpleSketchAPI(eng).background(*args)


def rect(x, y, w, h, **kwargs):
    eng = _get_engine()
    import core.shape as _shape
    return _shape.rect(eng, x, y, w, h, **kwargs)


def line(x1, y1, x2, y2, **kwargs):
    eng = _get_engine()
    import core.shape as _shape
    return _shape.line(eng, x1, y1, x2, y2, **kwargs)


def fill(*args):
    eng = _get_engine()
    from core.engine.api import SimpleSketchAPI
    return SimpleSketchAPI(eng).fill(*args)


def stroke(*args):
    eng = _get_engine()
    from core.engine.api import SimpleSketchAPI
    return SimpleSketchAPI(eng).stroke(*args)


def stroke_weight(w: int):
    eng = _get_engine()
    import core.shape as _shape
    return _shape.stroke_weight(eng, w)


def save_frame(path: str):
    eng = _get_engine()
    # Engine orchestrates snapshot backends; call the engine method.
    return eng._save_frame(path)


def frame_rate(n: int):
    eng = _get_engine()
    try:
        eng.frame_rate = int(n)
    except Exception:
        raise TypeError('frame_rate expects an integer')


def no_loop():
    eng = _get_engine()
    return eng._no_loop()


def loop():
    eng = _get_engine()
    return eng._loop()


def redraw():
    eng = _get_engine()
    return eng._redraw()


def hsb_to_rgb(h, s, b):
    from core.color import hsb_to_rgb as _h
    return _h(h, s, b)


# Note: `width` and `height` are exposed as dynamic module attributes
# via `__getattr__` below (so `pycreative.width` and `pycreative.height`
# return the current engine values). Do not define callables with these
# names as that prevents `__getattr__` from being called.


# Module-level dynamic attributes: expose `width` and `height` as attributes
# (not callables) so users can write `pycreative.width` / `pycreative.height`.
def __getattr__(name: str):
    """Provide dynamic module attributes such as `width` and `height`.

    Accessing `pycreative.width` or `pycreative.height` returns values from
    the currently registered engine (set via `set_current_engine`).
    """
    if name == 'width':
        try:
            eng = get_current_engine()
        except Exception:
            raise AttributeError('width is not available until an engine is set')
        from core.environment import width as _w
        return _w(eng)
    if name == 'height':
        try:
            eng = get_current_engine()
        except Exception:
            raise AttributeError('height is not available until an engine is set')
        from core.environment import height as _hgt
        return _hgt(eng)
    raise AttributeError(name)


def __dir__():
    """List module attributes, including dynamic `width`/`height`."""
    # include dynamic attributes
    return sorted(list(globals().keys()) + ['width', 'height'])


# Public shims
# previously the public shim functions were defined below; they are now
# replaced by the explicit implementations above.
