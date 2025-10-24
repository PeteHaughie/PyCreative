"""Random helpers (per-engine RNG and noise) extracted from package init.

Keep implementations here; `src/core/random/__init__.py` will remain a thin
re-export to avoid heavy imports at package import time.
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
    rng = _ensure_rng(engine)
    try:
        return rng.uniform(float(low), float(high))
    except Exception:
        return float(low) + rng.random() * (float(high) - float(low))


def random_seed(engine: Any, seed):
    try:
        r = _random.Random(int(seed))
    except Exception:
        r = _random.Random()
    setattr(engine, '_rand', r)
    return None


def random_gaussian(engine: Any):
    rng = _ensure_rng(engine)
    try:
        return rng.gauss(0.0, 1.0)
    except Exception:
        u1 = rng.random()
        u2 = rng.random()
        z0 = math.sqrt(-2.0 * math.log(max(u1, 1e-12))) * math.cos(2.0 * math.pi * u2)
    return z0


# Noise helpers
def _ensure_noise_state(engine: Any):
    st = getattr(engine, '_noise_state', None)
    if st is None:
        # Keep state keys compatible with previous implementation but
        # also store perlin-array style state to match Processing's
        # reference implementation semantics.
        st = {'perm': None, 'octaves': 4, 'falloff': 0.5,
              'perlin': None, 'perlin_random': None}
        setattr(engine, '_noise_state', st)
    return st


def noise_seed(engine: Any, seed: int):
    # Seed both the permutation-based state (kept for compatibility)
    # and the Processing-style `perlin` array RNG so `noise()` is
    # reproducible and behaves like Processing when `noiseSeed` is used.
    try:
        r = _random.Random(int(seed))
    except Exception:
        r = _random.Random()
    perm = list(range(256))
    r.shuffle(perm)
    perm = perm * 2
    st = _ensure_noise_state(engine)
    st['perm'] = perm
    # store a dedicated RNG for perlin array construction and reset
    st['perlin_random'] = _random.Random(int(seed)) if seed is not None else _random.Random()
    # force perlin array rebuild on next noise() call
    st['perlin'] = None
    return None


def _fade(t: float) -> float:
    return t * t * t * (t * (t * 6 - 15) + 10)


def _grad(hash_val: int, x: float, y: float = 0.0, z: float = 0.0) -> float:
    h = hash_val & 15
    u = x if h < 8 else y
    v = y if h < 4 else (x if h in (12, 14) else z)
    return ((u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v))


def _noise3d_from_perm(perm, x: float, y: float = 0.0, z: float = 0.0) -> float:
    xi = int(math.floor(x)) & 255
    yi = int(math.floor(y)) & 255
    zi = int(math.floor(z)) & 255
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

    res = y1 * (1 - w) + y2 * w
    return (res + 1) / 2


def noise(engine: Any, x: float, y: float = 0.0, z: float = 0.0) -> float:
    # Implement a Processing-compatible Perlin noise implementation
    # (the "toxi" / farbrausch variant). This keeps the external API
    # stable (noise, noise_detail, noise_seed) but matches the
    # characteristic output Processing users expect.
    st = _ensure_noise_state(engine)

    # Processing constants
    PERLIN_YWRAPB = 4
    PERLIN_YWRAP = 1 << PERLIN_YWRAPB
    PERLIN_ZWRAPB = 8
    PERLIN_ZWRAP = 1 << PERLIN_ZWRAPB
    PERLIN_SIZE = 4095

    perlin = st.get('perlin')
    prng = st.get('perlin_random')
    if perlin is None:
        # Build the perlin array using the engine RNG where possible
        if prng is None:
            prng = _random.Random()
            st['perlin_random'] = prng
        perlin = [prng.random() for _ in range(PERLIN_SIZE + 1)]
        st['perlin'] = perlin

    # ensure non-negative coordinates as Processing does
    try:
        if x < 0:
            x = -x
    except Exception:
        x = float(x)
    try:
        if y < 0:
            y = -y
    except Exception:
        y = float(y)
    try:
        if z < 0:
            z = -z
    except Exception:
        z = float(z)

    xi = int(math.floor(x))
    yi = int(math.floor(y))
    zi = int(math.floor(z))
    xf = x - math.floor(x)
    yf = y - math.floor(y)
    zf = z - math.floor(z)

    # Use the faster quintic fade function for interpolation. This is
    # numerically similar to cosine interpolation but avoids expensive
    # math.cos calls and is commonly used in performant Perlin variants.
    # The helper `_fade` is defined above and implements the polynomial.

    r = 0.0
    ampl = 0.5

    octaves = st.get('octaves', 4)
    falloff = st.get('falloff', 0.5)

    for _ in range(int(octaves)):
        of = xi + (yi << PERLIN_YWRAPB) + (zi << PERLIN_ZWRAPB)

        rxf = _fade(xf)
        ryf = _fade(yf)

        n1 = perlin[of & PERLIN_SIZE]
        n1 = n1 + rxf * (perlin[(of + 1) & PERLIN_SIZE] - n1)
        n2 = perlin[(of + PERLIN_YWRAP) & PERLIN_SIZE]
        n2 = n2 + rxf * (perlin[(of + PERLIN_YWRAP + 1) & PERLIN_SIZE] - n2)
        n1 = n1 + ryf * (n2 - n1)

        of += PERLIN_ZWRAP
        n2 = perlin[of & PERLIN_SIZE]
        n2 = n2 + rxf * (perlin[(of + 1) & PERLIN_SIZE] - n2)
        n3 = perlin[(of + PERLIN_YWRAP) & PERLIN_SIZE]
        n3 = n3 + rxf * (perlin[(of + PERLIN_YWRAP + 1) & PERLIN_SIZE] - n3)
        n2 = n2 + ryf * (n3 - n2)

        n1 = n1 + _fade(zf) * (n2 - n1)

        r += n1 * ampl
        ampl *= falloff

        xi <<= 1
        xf *= 2.0
        yi <<= 1
        yf *= 2.0
        zi <<= 1
        zf *= 2.0

        if xf >= 1.0:
            xi += 1
            xf -= 1.0
        if yf >= 1.0:
            yi += 1
            yf -= 1.0
        if zf >= 1.0:
            zi += 1
            zf -= 1.0

    return r


def noise_detail(engine: Any, lod: int, falloff: float = 0.5):
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


def noise_field(engine: Any, width: int, height: int, x0: float = 0.0, y0: float = 0.0, z0: float = 0.0, inc: float = 0.02):
    """Compute a full noise field (width x height) as a numpy uint8 array.

    This function uses numpy when available to vectorize the Perlin
    sampling across the whole grid and is orders of magnitude faster than
    calling `noise()` in a Python inner loop. It returns a 2D numpy array
    of dtype uint8 with values in [0,255]. If numpy is not available, the
    function returns None.
    """
    try:
        import numpy as np
    except Exception:
        return None

    st = _ensure_noise_state(engine)
    perlin = st.get('perlin')
    prng = st.get('perlin_random')
    if perlin is None:
        if prng is None:
            prng = _random.Random()
            st['perlin_random'] = prng
        perlin = [prng.random() for _ in range(4095 + 1)]
        st['perlin'] = perlin

    perlin_np = np.asarray(perlin, dtype=float)

    # Processing constants (match noise() above)
    PERLIN_YWRAPB = 4
    PERLIN_YWRAP = 1 << PERLIN_YWRAPB
    PERLIN_ZWRAPB = 8
    PERLIN_ZWRAP = 1 << PERLIN_ZWRAPB
    PERLIN_SIZE = 4095

    try:
        octaves = int(st.get('octaves', 4))
    except Exception:
        octaves = 4
    try:
        falloff = float(st.get('falloff', 0.5))
    except Exception:
        falloff = 0.5

    # Create coordinate grids. Use 1-based offsets to match existing sketches
    xs = x0 + (np.arange(width) + 1) * float(inc)
    ys = y0 + (np.arange(height) + 1) * float(inc)
    X, Y = np.meshgrid(xs, ys)
    Z = float(z0)

    # Ensure non-negative coords, like noise()
    X = np.abs(X)
    Y = np.abs(Y)
    Z = abs(Z)

    # initialize accumulators
    r = np.zeros_like(X, dtype=float)
    ampl = 0.5

    xi = np.floor(X).astype(np.int64)
    yi = np.floor(Y).astype(np.int64)
    zi = int(math.floor(Z))
    xf = X - np.floor(X)
    yf = Y - np.floor(Y)
    zf = Z - math.floor(Z)

    for _ in range(octaves):
        of = xi + (yi << PERLIN_YWRAPB) + (zi << PERLIN_ZWRAPB)

        rxf = _fade(xf)
        ryf = _fade(yf)

        n1 = perlin_np[of & PERLIN_SIZE]
        n1 = n1 + rxf * (perlin_np[(of + 1) & PERLIN_SIZE] - n1)
        n2 = perlin_np[(of + PERLIN_YWRAP) & PERLIN_SIZE]
        n2 = n2 + rxf * (perlin_np[(of + PERLIN_YWRAP + 1) & PERLIN_SIZE] - n2)
        n1 = n1 + ryf * (n2 - n1)

        of2 = of + PERLIN_ZWRAP
        n2 = perlin_np[of2 & PERLIN_SIZE]
        n2 = n2 + rxf * (perlin_np[(of2 + 1) & PERLIN_SIZE] - n2)
        n3 = perlin_np[(of2 + PERLIN_YWRAP) & PERLIN_SIZE]
        n3 = n3 + rxf * (perlin_np[(of2 + PERLIN_YWRAP + 1) & PERLIN_SIZE] - n3)
        n2 = n2 + ryf * (n3 - n2)

        n1 = n1 + _fade(zf) * (n2 - n1)

        r += n1 * ampl
        ampl *= falloff

        # advance octave (elementwise)
        xi = xi << 1
        xf = xf * 2.0
        yi = yi << 1
        yf = yf * 2.0
        # zi and zf: zi is scalar
        zi = zi << 1
        zf = zf * 2.0

        # wrap fractional parts >=1
        m = xf >= 1.0
        if m.any():
            xi = xi + m.astype(np.int64)
            xf = xf - m.astype(float)
        m = yf >= 1.0
        if m.any():
            yi = yi + m.astype(np.int64)
            yf = yf - m.astype(float)
        if zf >= 1.0:
            zi += 1
            zf -= 1.0

    # r is in similar range to noise(); clamp to [0,1] and convert to uint8
    try:
        out = np.clip(r, 0.0, 1.0)
        out = (out * 255.0).astype(np.uint8)
    except Exception:
        out = None
    return out


__all__ = [
    "random",
    "random_seed",
    "random_gaussian",
    "uniform",
    "noise",
    "noise_seed",
    "noise_detail",
    "noise_field",
]
