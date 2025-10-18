"""Math helpers used by sketches (pure functions).

This module provides the numeric helpers from the former
`src/core/math/__init__.py`. Keep implementations small and importable
without pulling vector class definitions.
"""
from __future__ import annotations

import builtins
import math


def abs_(v: float) -> float:
    return abs(v)


def ceil(v: float) -> int:
    return math.ceil(v)


def floor(v: float) -> int:
    return math.floor(v)


def constrain(v: float, low: float, high: float) -> float:
    return max(min(v, high), low)


def dist(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.hypot(x2 - x1, y2 - y1)


def lerp(start: float, stop: float, amt: float) -> float:
    return (1.0 - amt) * start + amt * stop


def mag(x: float, y: float) -> float:
    return math.hypot(x, y)


def map_(value: float, start1: float, stop1: float, start2: float, stop2: float) -> float:
    # Avoid division by zero
    if stop1 == start1:
        raise ValueError('map: start1 and stop1 cannot be equal')
    return start2 + (value - start1) * (stop2 - start2) / (stop1 - start1)


def sq(v: float) -> float:
    return v * v


def sqrt(v: float) -> float:
    return math.sqrt(v)


def sin(v: float) -> float:
    return math.sin(v)


def cos(v: float) -> float:
    return math.cos(v)


def tan(v: float) -> float:
    return math.tan(v)


def radians(deg: float) -> float:
    return math.radians(deg)


def degrees(rad: float) -> float:
    return math.degrees(rad)


def pow_(a: float, b: float) -> float:
    return math.pow(a, b)


def max_(a: float, b: float) -> float:
    return a if a >= b else b


def min_(a: float, b: float) -> float:
    return a if a <= b else b


def round_(v: float) -> int:
    # Use the builtin round to avoid accidentally calling the module-level
    # `round` alias and causing recursion.
    return builtins.round(v)


# Public aliases (these are re-exported by package __init__)
abs = abs_
map = map_
pow = pow_
max = max_
min = min_
round = round_
