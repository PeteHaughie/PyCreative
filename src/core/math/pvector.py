"""PCVector: a tiny 2D vector type used by sketches.

This module contains the PCVector class and related vector helpers.
"""
from __future__ import annotations

import math
from typing import Tuple


class PCVector:
    """Tiny 2D vector used by sketches (subset of Processing's PVector)."""

    __slots__ = ('x', 'y')

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)

    def set(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def mag(self) -> float:
        return math.hypot(self.x, self.y)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f'PCVector({self.x}, {self.y})'

    def copy(self) -> 'PCVector':
        return PCVector(self.x, self.y)

    @staticmethod
    def sub_vec(a, b):
        ax, ay = (a.x, a.y) if isinstance(a, PCVector) else (float(a[0]), float(a[1]))
        bx, by = (b.x, b.y) if isinstance(b, PCVector) else (float(b[0]), float(b[1]))
        return PCVector(ax - bx, ay - by)

    @staticmethod
    def add_vec(a, b):
        ax, ay = (a.x, a.y) if isinstance(a, PCVector) else (float(a[0]), float(a[1]))
        bx, by = (b.x, b.y) if isinstance(b, PCVector) else (float(b[0]), float(b[1]))
        return PCVector(ax + bx, ay + by)

    @staticmethod
    def mult_vec(a, n):
        ax, ay = (a.x, a.y) if isinstance(a, PCVector) else (float(a[0]), float(a[1]))
        if isinstance(n, PCVector):
            return PCVector(ax * n.x, ay * n.y)
        nf = float(n)
        return PCVector(ax * nf, ay * nf)

    @staticmethod
    def div_vec(a, n):
        ax, ay = (a.x, a.y) if isinstance(a, PCVector) else (float(a[0]), float(a[1]))
        if isinstance(n, PCVector):
            if n.x == 0 or n.y == 0:
                raise ZeroDivisionError('division by zero component in vector')
            return PCVector(ax / n.x, ay / n.y)
        nf = float(n)
        if nf == 0:
            raise ZeroDivisionError('division by zero')
        return PCVector(ax / nf, ay / nf)

    @staticmethod
    def from_angle(angle: float, magnitude: float = 1.0) -> 'PCVector':
        return PCVector(math.cos(angle) * magnitude, math.sin(angle) * magnitude)

    @staticmethod
    def random2d(magnitude: float = 1.0) -> 'PCVector':
        try:
            import random as _r
            angle = _r.random() * 2.0 * math.pi
            return PCVector.from_angle(angle, float(magnitude))
        except Exception:
            return PCVector.from_angle(0.0, float(magnitude))

    def _unpack_other(self, other, y=None) -> Tuple[float, float]:
        if isinstance(other, PCVector):
            return other.x, other.y
        if isinstance(other, tuple) or isinstance(other, list):
            if len(other) != 2:
                raise ValueError('tuple/list must have length 2')
            return float(other[0]), float(other[1])
        if y is None:
            raise TypeError('Expected PCVector or (x, y) pair when y is None')
        return float(other), float(y)

    def add(self, other, y=None):
        ox, oy = self._unpack_other(other, y)
        self.x += ox
        self.y += oy
        return self

    def sub(self, other, y=None):
        ox, oy = self._unpack_other(other, y)
        self.x -= ox
        self.y -= oy
        return self

    def mult(self, n):
        if isinstance(n, PCVector):
            self.x *= n.x
            self.y *= n.y
        else:
            self.x *= float(n)
            self.y *= float(n)
        return self

    def div(self, n):
        if isinstance(n, PCVector):
            if n.x == 0 or n.y == 0:
                raise ZeroDivisionError('division by zero component in vector')
            self.x /= n.x
            self.y /= n.y
        else:
            n = float(n)
            if n == 0:
                raise ZeroDivisionError('division by zero')
            self.x /= n
            self.y /= n
        return self

    def normalize(self):
        m = self.mag()
        if m != 0:
            self.x /= m
            self.y /= m
        return self

    def set_mag(self, magnitude: float):
        self.normalize()
        self.mult(magnitude)
        return self

    def limit(self, max_len: float):
        m = self.mag()
        if m > float(max_len):
            self.set_mag(float(max_len))

    def dot(self, other: 'PCVector') -> float:
        return self.x * other.x + self.y * other.y

    def heading(self) -> float:
        return math.atan2(self.y, self.x)

    def rotate(self, angle: float):
        c = math.cos(angle)
        s = math.sin(angle)
        nx = self.x * c - self.y * s
        ny = self.x * s + self.y * c
        self.x = nx
        self.y = ny

    def lerp(self, target: 'PCVector', amt: float):
        from .ops import lerp
        self.x = lerp(self.x, target.x, amt)
        self.y = lerp(self.y, target.y, amt)

    def distance(self, other: 'PCVector') -> float:
        from .ops import dist
        return dist(self.x, self.y, other.x, other.y)

    def __add__(self, other):
        if isinstance(other, PCVector):
            return PCVector(self.x + other.x, self.y + other.y)
        return PCVector(self.x + float(other), self.y + float(other))

    def __sub__(self, other):
        if isinstance(other, PCVector):
            return PCVector(self.x - other.x, self.y - other.y)
        return PCVector(self.x - float(other), self.y - float(other))

    def __mul__(self, other):
        if isinstance(other, PCVector):
            return PCVector(self.x * other.x, self.y * other.y)
        return PCVector(self.x * float(other), self.y * float(other))

    def __truediv__(self, other):
        if isinstance(other, PCVector):
            if other.x == 0 or other.y == 0:
                raise ZeroDivisionError('division by zero component in vector')
            return PCVector(self.x / other.x, self.y / other.y)
        other = float(other)
        if other == 0:
            raise ZeroDivisionError('division by zero')
        return PCVector(self.x / other, self.y / other)

    def __neg__(self):
        return PCVector(-self.x, -self.y)

    def __eq__(self, other) -> bool:
        if not isinstance(other, PCVector):
            return False
        return self.x == other.x and self.y == other.y


# Convenience module-level helpers mirroring Processing-style API
def sub(a, b):
    return PCVector.sub_vec(a, b)


def add(a, b):
    return PCVector.add_vec(a, b)


def mult(a, n):
    return PCVector.mult_vec(a, n)


def div(a, n):
    return PCVector.div_vec(a, n)
