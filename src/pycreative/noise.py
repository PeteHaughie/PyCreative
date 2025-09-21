"""
pycreative.noise: Noise utilities for creative coding (Perlin, etc.)
"""

import math
import random
from typing import Optional


class PerlinNoise:
    """
    Simple Perlin noise implementation for 1D and 2D.
    Usage:
        noise = PerlinNoise(seed=42)
        val = noise.noise1d(x)
        val2d = noise.noise2d(x, y)
    """

    def __init__(self, seed: Optional[int] = None):
        self.permutation = list(range(256))
        if seed is not None:
            random.seed(seed)
        random.shuffle(self.permutation)
        self.permutation += self.permutation

    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, a, b, t):
        return a + t * (b - a)

    def grad(self, hash, x: float, y: float = 0.0) -> float:
        h = hash & 15
        u = x if h < 8 else y
        v = y if h < 4 else (x if h in (12, 14) else 0)
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

    def noise1d(self, x: float) -> float:
        xi = int(math.floor(x)) & 255
        xf = x - math.floor(x)
        u = self.fade(xf)
        a = self.permutation[xi]
        b = self.permutation[xi + 1]
        return self.lerp(self.grad(a, xf), self.grad(b, xf - 1), u)

    def noise2d(self, x: float, y: float) -> float:
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        xf = x - math.floor(x)
        yf = y - math.floor(y)
        u = self.fade(xf)
        v = self.fade(yf)
        aa = self.permutation[self.permutation[xi] + yi]
        ab = self.permutation[self.permutation[xi] + yi + 1]
        ba = self.permutation[self.permutation[xi + 1] + yi]
        bb = self.permutation[self.permutation[xi + 1] + yi + 1]
        x1 = self.lerp(self.grad(aa, xf, yf), self.grad(ba, xf - 1, yf), u)
        x2 = self.lerp(self.grad(ab, xf, yf - 1), self.grad(bb, xf - 1, yf - 1), u)
        return self.lerp(x1, x2, v)
