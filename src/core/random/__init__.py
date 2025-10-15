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
    if len(args) == 1:
        high = float(args[0])
        return rng.random() * high
    elif len(args) == 2:
        low = float(args[0])
        high = float(args[1])
        return low + rng.random() * (high - low)
    else:
        raise TypeError('random() expects 1 or 2 arguments')


def random_seed(engine: Any, seed):
    """Seed the per-engine RNG for deterministic sequences."""
    try:
        r = _random.Random(int(seed))
    except Exception:
        r = _random.Random()
    setattr(engine, '_rand', r)
    return None

__all__ = ["random", "random_seed"]
