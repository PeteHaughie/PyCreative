"""Small Processing-like math facade for pycreative.

Expose a tiny set of math helpers and constants used by sketches. This
module keeps a stable surface for examples/tests so code can import
`self.math` from a Sketch instance without accidentally shadowing the
stdlib `math` module.
"""
from __future__ import annotations

from typing import Any

import math as _math

# Re-export commonly used functions with the same names Processing sketches
# expect. These are thin wrappers around Python's stdlib math functions.
PI = _math.pi
TWO_PI = 2.0 * _math.pi
HALF_PI = 0.5 * _math.pi

cos = _math.cos
sin = _math.sin
tan = _math.tan
atan2 = _math.atan2
sqrt = _math.sqrt
pow = _math.pow
floor = _math.floor
ceil = _math.ceil
radians = _math.radians
degrees = _math.degrees

# Keep a reference to the raw math module for callers that want the full API
raw: Any = _math

__all__ = [
    "PI",
    "TWO_PI",
    "HALF_PI",
    "cos",
    "sin",
    "tan",
    "atan2",
    "sqrt",
    "pow",
    "floor",
    "ceil",
    "radians",
    "degrees",
    "raw",
]
