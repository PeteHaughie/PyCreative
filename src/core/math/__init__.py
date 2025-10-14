"""Math helpers used by sketches.

This module implements a small subset of the Processing-style math API.
Functions accept and return plain Python numbers. PCVector is a tiny 2D
vector with a few convenience methods.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Tuple


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
    return round(v)


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

    def add(self, other: 'PCVector'):
        self.x += other.x
        self.y += other.y

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f'PCVector({self.x}, {self.y})'

    # --- Extended API (Processing-like helpers) ---
    def copy(self) -> 'PCVector':
        return PCVector(self.x, self.y)

    @staticmethod
    def from_angle(angle: float, magnitude: float = 1.0) -> 'PCVector':
        return PCVector(math.cos(angle) * magnitude, math.sin(angle) * magnitude)

    def _unpack_other(self, other, y=None) -> Tuple[float, float]:
        # Accept another PCVector, a (x,y) tuple, or numeric x with y provided
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

    def sub(self, other, y=None):
        ox, oy = self._unpack_other(other, y)
        self.x -= ox
        self.y -= oy

    def mult(self, n):
        # multiply by scalar or component-wise by another vector
        if isinstance(n, PCVector):
            self.x *= n.x
            self.y *= n.y
        else:
            self.x *= float(n)
            self.y *= float(n)

    def div(self, n):
        # divide by scalar or component-wise by another vector
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

    def normalize(self):
        m = self.mag()
        if m != 0:
            self.x /= m
            self.y /= m

    def set_mag(self, magnitude: float):
        self.normalize()
        self.mult(magnitude)

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
        self.x = lerp(self.x, target.x, amt)
        self.y = lerp(self.y, target.y, amt)

    def distance(self, other: 'PCVector') -> float:
        return dist(self.x, self.y, other.x, other.y)

    # Operator overloads returning new vectors
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


# Public aliases to match API map names (safe to shadow builtins inside module)
abs = abs_
map = map_
pow = pow_
max = max_
min = min_
round = round_
