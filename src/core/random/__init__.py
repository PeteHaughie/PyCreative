"""Random helpers implementing Processing-style random()/random_seed().

These functions operate on a per-engine RNG stored as `engine._rand` so
calling `random_seed(engine, s)` yields deterministic sequences for that
engine without interfering with other engines or global state.
"""
from __future__ import annotations

import math
import random as _random
from typing import Any


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


def uniform(engine: Any, low: float, high: float) -> float:
    """Return a random float N such that low <= N <= high using the engine RNG."""
    rng = _ensure_rng(engine)
    try:
        return rng.uniform(float(low), float(high))
    except Exception:
        # fallback to scaled random
        return float(low) + rng.random() * (float(high) - float(low))


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


# --- Simple Perlin noise implementation (1D/2D/3D) ---
# This is a small self-contained implementation to avoid adding
# external dependencies. It supports per-engine permutation tables so
# noise_seed(engine, s) yields deterministic noise for that engine.


def _ensure_noise_state(engine: Any):
    st = getattr(engine, '_noise_state', None)
    if st is None:
        # default: 4 octaves, falloff 0.5
        st = {'perm': None, 'octaves': 4, 'falloff': 0.5}
        setattr(engine, '_noise_state', st)
    return st


def noise_seed(engine: Any, seed: int):
    """Seed the per-engine noise permutation table for deterministic noise."""
    try:
        r = _random.Random(int(seed))
    except Exception:
        r = _random.Random()
    perm = list(range(256))
    r.shuffle(perm)
    # duplicate to avoid overflow indexing
    perm = perm * 2
    st = _ensure_noise_state(engine)
    st['perm'] = perm
    return None


def _fade(t: float) -> float:
    # classic fade curve 6t^5 - 15t^4 + 10t^3
    return t * t * t * (t * (t * 6 - 15) + 10)


def _grad(hash_val: int, x: float, y: float = 0.0, z: float = 0.0) -> float:
    h = hash_val & 15
    u = x if h < 8 else y
    v = y if h < 4 else (x if h in (12, 14) else z)
    return ((u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v))


def _noise3d_from_perm(perm, x: float, y: float = 0.0, z: float = 0.0) -> float:
    # Find unit cube that contains point
    xi = int(math.floor(x)) & 255
    yi = int(math.floor(y)) & 255
    zi = int(math.floor(z)) & 255
    # Find relative x,y,z of point in cube
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    zf = z - math.floor(z)
    u = _fade(xf)
    v = _fade(yf)
    w = _fade(zf)

    aaa = perm[perm[perm[xi] + yi] + zi]
    aba = perm[perm[perm[xi] + yi + 1] + zi]
    aab = perm[perm[perm[xi] + yi] + zi + 1]
    abb = perm[perm[perm[xi] + yi + 1] + zi + 1]
    baa = perm[perm[perm[xi + 1] + yi] + zi]
    bba = perm[perm[perm[xi + 1] + yi + 1] + zi]
    bab = perm[perm[perm[xi + 1] + yi] + zi + 1]
    bbb = perm[perm[perm[xi + 1] + yi + 1] + zi + 1]

    x1 = (_grad(aaa, xf, yf, zf) * (1 - u) + _grad(baa, xf - 1, yf, zf) * u)
    x2 = (_grad(aba, xf, yf - 1, zf) * (1 - u) + _grad(bba, xf - 1, yf - 1, zf) * u)
    y1 = x1 * (1 - v) + x2 * v

    x3 = (_grad(aab, xf, yf, zf - 1) * (1 - u) + _grad(bab, xf - 1, yf, zf - 1) * u)
    x4 = (_grad(abb, xf, yf - 1, zf - 1) * (1 - u) + _grad(bbb, xf - 1, yf - 1, zf - 1) * u)
    y2 = x3 * (1 - v) + x4 * v

    # Interpolate along z
    res = y1 * (1 - w) + y2 * w
    # Normalize result to [0,1]
    return (res + 1) / 2


def noise(engine: Any, x: float, y: float = 0.0, z: float = 0.0) -> float:
    """Return Perlin noise value in [0,1] at (x[, y[, z]]).

    Uses per-engine permutation table seeded by noise_seed(). If the table
    doesn't exist yet, create one using Python's global random.
    """
    st = _ensure_noise_state(engine)
    perm = st.get('perm')
    if perm is None:
        # create a default perm table
        r = _random.Random()
        p = list(range(256))
        r.shuffle(p)
        perm = p * 2
        st['perm'] = perm

    octaves = st.get('octaves', 4)
    falloff = st.get('falloff', 0.5)

    total = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_amplitude = 0.0
    for _ in range(int(octaves)):
        val = _noise3d_from_perm(perm, x * frequency, y * frequency, z * frequency)
        total += val * amplitude
        max_amplitude += amplitude
        amplitude *= falloff
        frequency *= 2.0

    # Normalize to [0,1]
    if max_amplitude == 0:
        return 0.0
    return total / max_amplitude


def noise_detail(engine: Any, lod: int, falloff: float = 0.5):
    """Adjust number of octaves (lod) and falloff for the engine's noise()."""
    st = _ensure_noise_state(engine)
    try:
        st['octaves'] = int(lod)
    except Exception:
        pass
    try:
        st['falloff'] = float(falloff)
    except Exception:
        pass
    return None


__all__ = ["random", "random_seed", "random_gaussian", "uniform", "noise", "noise_seed", "noise_detail"]
