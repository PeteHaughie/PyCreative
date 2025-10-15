"""Random helpers implementing Processing-style random()/random_seed().

These functions operate on a per-engine RNG stored as `engine._rand` so
calling `random_seed(engine, s)` yields deterministic sequences for that
engine without interfering with other engines or global state.
"""
from __future__ import annotations

from typing import Any
import random as _random


def _ensure_rng(engine: Any):
    r = getattr(engine, '_rand', None)
    if r is None:
        r = _random.Random()
        setattr(engine, '_rand', r)
    return r


def random(engine: Any, *args):
    """random(high) -> float in [0, high)
    random(low, high) -> float in [low, high)
    """
    rng = _ensure_rng(engine)
    # Support Processing-compatible overloads: zero args -> [0,1),
    # one arg -> [0, high), two args -> [low, high).
    if len(args) == 0:
        return rng.random()
    if len(args) == 1:
        high = float(args[0])
        return rng.random() * high
    if len(args) == 2:
        low = float(args[0])
        high = float(args[1])
        return low + rng.random() * (high - low)
    raise TypeError('random() expects 0, 1 or 2 arguments')


def random_seed(engine: Any, seed):
    """Seed the per-engine RNG for deterministic sequences."""
    try:
        r = _random.Random(int(seed))
    except Exception:
        r = _random.Random()
    setattr(engine, '_rand', r)
    return None


def random_gaussian(engine: Any):
    """Return a Gaussian-distributed float with mean 0 and stddev 1 using the
    engine's RNG. Mirrors Processing's randomGaussian()."""
    rng = _ensure_rng(engine)
    try:
        return rng.gauss(0.0, 1.0)
    except Exception:
        # Fallback: use Box-Muller with random() if gauss isn't available
        u1 = rng.random()
        u2 = rng.random()
        import math
        z0 = math.sqrt(-2.0 * math.log(max(u1, 1e-12))) * math.cos(2.0 * math.pi * u2)
        return z0

__all__ = ["random", "random_seed", "random_gaussian"]
