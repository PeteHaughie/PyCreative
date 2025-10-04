"""Pure-Python Perlin noise implementation (1D) with optional seeding.

This module provides a lightweight PerlinNoise class and convenience
functions `noise(x)` and `seed(s)` backed by a module-level instance.

The noise output is normalized to the range [0, 1], which matches
Processing's noise() expectations for examples in this repository.
"""
from __future__ import annotations

from typing import Optional
import math
import random


class PerlinNoise:
    """A minimal 1D Perlin noise generator.

    Uses a shuffled permutation table seeded via the provided integer seed.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rand = random.Random(seed)
        # Classic Perlin uses a 256-entry permutation table duplicated
        p = list(range(256))
        self._rand.shuffle(p)
        self.perm = p + p

    @staticmethod
    def _fade(t: float) -> float:
        # 6t^5 - 15t^4 + 10t^3
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        return a + t * (b - a)

    @staticmethod
    def _grad(hashval: int, x: float) -> float:
        # 1D gradient: use the lowest bit to choose direction
        return x if (hashval & 1) == 0 else -x

    def noise1d(self, x: float) -> float:
        """Compute 1D Perlin noise for coordinate x. Returns value in [0,1]."""
        # Find unit grid cell containing point
        xi = math.floor(x) & 255
        xf = x - math.floor(x)

        u = self._fade(xf)

        a = self.perm[xi]
        b = self.perm[xi + 1]

        # Gradients at lattice points
        ga = self._grad(a, xf)
        gb = self._grad(b, xf - 1)

        # Interpolate between gradients
        val = self._lerp(ga, gb, u)

        # Perlin output is typically in -1..1; normalize to 0..1
        return (val + 1.0) * 0.5


# Module-level default generator
_default = PerlinNoise()


def noise(x: float) -> float:
    """Convenience function: compute 1D noise using the module default."""
    return _default.noise1d(float(x))


def seed(s: Optional[int]) -> None:
    """Reseed the module-level noise generator. Pass None to reseed randomly."""
    global _default
    _default = PerlinNoise(s)
