"""Event dispatch helpers for invoking sketch handlers.

Provides a small helper to call sketch-provided functions with the
conservative semantics used by the Engine: prefer calling with a `this`
facade, but handle bound methods and TypeError fallbacks.
"""
from typing import Any, Callable


def call_sketch_method(fn: Callable, this: Any):
    """Call a sketch-provided callable using the Engine's semantics.

    Behaviour:
    - If fn is a bound method (has __self__), call without args.
    - Otherwise, prefer calling fn(this). If that raises TypeError,
      fall back to fn().
    """
    try:
        bound_self = getattr(fn, '__self__', None)
        if bound_self is not None:
            return fn()
    except Exception:
        pass

    try:
        return fn(this)
    except TypeError:
        return fn()
