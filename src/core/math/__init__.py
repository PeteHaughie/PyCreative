"""Thin re-export for math helpers and PCVector.

Keep implementation in `ops.py` and `pcvector.py` so importing `core.math`
is lightweight and explicit.
"""
from __future__ import annotations

# Re-export submodules and public names
from . import ops
from . import pcvector

__all__ = [
    # submodules
    'ops',
    'pcvector',
    # numeric helpers
    'ceil',
    'floor',
    'constrain',
    'dist',
    'lerp',
    'mag',
    'map',
    'map_',
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
    'pow_',
    'max',
    'max_',
    'min',
    'min_',
    'round',
    'round_',
    # vector/type exports
    'PCVector',
    # vector helpers
    'sub',
    'add',
    'mult',
    'div',
]

# Pull a few commonly used symbols into package namespace for compatibility
# Re-export commonly used numeric helpers at package level for backwards compat
from .ops import abs, map, map_, pow, pow_, max, max_, min, min_, round, round_
from .pcvector import PCVector
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
from .pcvector import sub, add, mult, div
