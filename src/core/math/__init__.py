"""Thin re-export for math helpers and PCVector.

Keep implementation in `ops.py` and `pvector.py` so importing `core.math`
is lightweight and explicit.
"""
from __future__ import annotations

# Re-export submodules and public names
from . import ops
from . import pvector

__all__ = [
    # submodules
    'ops',
    'pvector',
    # numeric helpers
    'ceil',
    'floor',
    'constrain',
    'dist',
    'lerp',
    'mag',
    'map',
    'sq',
    'sqrt',
    'sin',
    'cos',
    'tan',
    'radians',
    'degrees',
    # common helpers aliased into package namespace for backwards compat
    'abs',
    'map',
    'pow',
    'max',
    'min',
    'round',
    # vector/type exports
    'PCVector',
    # vector helpers
    'sub',
    'add',
    'mult',
    'div',
]

# Pull a few commonly used symbols into package namespace for compatibility
from .ops import abs, map, pow, max, min, round
from .pvector import PCVector
# Re-export commonly used numeric helpers at package level for backwards compat
from .ops import (
    ceil,
    floor,
    constrain,
    dist,
    lerp,
    mag,
    sq,
    sqrt,
    sin,
    cos,
    tan,
    radians,
    degrees,
)

# Re-export small vector helpers
from .pvector import sub, add, mult, div
