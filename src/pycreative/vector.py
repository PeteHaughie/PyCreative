from __future__ import annotations

from typing import Iterator
import math
import random


class PVector:
    """A small Processing-like 2D vector class (PVector).

    Implements common vector operations used by Nature of Code examples.
    Methods follow Processing's PVector semantics where applicable: mutating
    methods return self to allow chaining; operator overloads return new
    PVectors.
    """

    __slots__ = ("x", "y")

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)

    # Sequence-style unpacking support so PVector works where (x,y) tuples are expected
    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    def copy(self) -> "PVector":
        return PVector(self.x, self.y)

    # Mutating operations (return self)
    def add(self, other) -> "PVector":
        ox, oy = (other.x, other.y) if isinstance(other, PVector) else (float(other[0]), float(other[1]))
        self.x += ox
        self.y += oy
        return self

    def set(self, x, y=None) -> "PVector":
        """Set this vector's components.

        Usage:
          v.set(other)          # other is a PVector or 2-length iterable
          v.set(x, y)           # x and y are numeric

        Returns self for chaining.
        """
        if isinstance(x, PVector):
            self.x = float(x.x)
            self.y = float(x.y)
            return self
        # allow a single 2-length iterable
        if y is None and hasattr(x, "__iter__"):
            vals = list(x)
            if len(vals) >= 2:
                self.x = float(vals[0])
                self.y = float(vals[1])
                return self
            raise TypeError("set() requires a 2-length iterable when a single argument is provided")

        if y is None:
            raise TypeError("set() requires two numeric arguments or a single PVector/iterable")

        self.x = float(x)
        self.y = float(y)
        return self

    def sub(self, other) -> "PVector":
        ox, oy = (other.x, other.y) if isinstance(other, PVector) else (float(other[0]), float(other[1]))
        self.x -= ox
        self.y -= oy
        return self

    def mult(self, scalar: float) -> "PVector":
        self.x *= float(scalar)
        self.y *= float(scalar)
        return self

    def div(self, scalar: float) -> "PVector":
        s = float(scalar)
        if s == 0.0:
            return self
        self.x /= s
        self.y /= s
        return self

    def mag(self) -> float:
        return math.hypot(self.x, self.y)

    def normalize(self) -> "PVector":
        m = self.mag()
        if m == 0.0:
            return self
        return self.div(m)

    def set_mag(self, m: float) -> "PVector":
        return self.normalize().mult(float(m))

    def limit(self, max_val: float) -> "PVector":
        m = self.mag()
        if m > max_val and m > 0.0:
            self.div(m)
            self.mult(max_val)
        return self

    def heading(self) -> float:
        return math.atan2(self.y, self.x)

    def rotate(self, theta: float) -> "PVector":
        c = math.cos(theta)
        s = math.sin(theta)
        x = self.x * c - self.y * s
        y = self.x * s + self.y * c
        self.x = x
        self.y = y
        return self

    def lerp(self, other, t: float) -> "PVector":
        ox, oy = (other.x, other.y) if isinstance(other, PVector) else (float(other[0]), float(other[1]))
        self.x = self.x + (ox - self.x) * float(t)
        self.y = self.y + (oy - self.y) * float(t)
        return self

    def dist(self, other) -> float:
        ox, oy = (other.x, other.y) if isinstance(other, PVector) else (float(other[0]), float(other[1]))
        dx = self.x - ox
        dy = self.y - oy
        return math.hypot(dx, dy)

    # Operator overloads (non-mutating)
    def __add__(self, other) -> "PVector":
        ox, oy = (other.x, other.y) if isinstance(other, PVector) else (float(other[0]), float(other[1]))
        return PVector(self.x + ox, self.y + oy)

    def __sub__(self, other) -> "PVector":
        ox, oy = (other.x, other.y) if isinstance(other, PVector) else (float(other[0]), float(other[1]))
        return PVector(self.x - ox, self.y - oy)

    def __mul__(self, scalar: float) -> "PVector":
        return PVector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> "PVector":
        s = float(scalar)
        if s == 0.0:
            return self.copy()
        return PVector(self.x / s, self.y / s)

    # Right-side operator overloads so Python will dispatch here when the
    # left operand doesn't know how to handle an operation (e.g., a tuple).
    # This makes expressions like (x,y) - PVector(...) or 2 * PVector(...) work
    # and prevents confusing TypeErrors for learners.
    def __radd__(self, other) -> "PVector":
        ox, oy = (other.x, other.y) if isinstance(other, PVector) else (float(other[0]), float(other[1]))
        return PVector(ox + self.x, oy + self.y)

    def __rsub__(self, other) -> "PVector":
        ox, oy = (other.x, other.y) if isinstance(other, PVector) else (float(other[0]), float(other[1]))
        return PVector(ox - self.x, oy - self.y)

    def __rmul__(self, scalar: float) -> "PVector":
        # support scalar * PVector
        try:
            s = float(scalar)
        except Exception:
            # if a 2-length iterable was provided, fall back to elementwise
            if isinstance(scalar, (tuple, list)):
                vals = list(scalar)
                if len(vals) >= 2:
                    return PVector(float(vals[0]) * self.x, float(vals[1]) * self.y)
            raise TypeError("Unsupported operand type(s) for *: '{}' and 'PVector'".format(type(scalar).__name__))
        return PVector(self.x * s, self.y * s)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"PVector({self.x!r}, {self.y!r})"

    # Convenience creators
    @classmethod
    def from_angle(cls, theta: float, target: "PVector | None" = None) -> "PVector":
        """Create a unit PVector from an angle (radians).

        If `target` is provided it will be mutated and returned (mirrors
        Processing's `PVector.fromAngle(angle, target)` convenience).
        """
        x = math.cos(theta)
        y = math.sin(theta)
        if target is None:
            return cls(x, y)
        target.x = float(x)
        target.y = float(y)
        return target

    # CamelCase alias for Processing-style API
    # Note: prefer snake_case API in this project; do not expose camelCase aliases.

    @classmethod
    def random2d(cls) -> "PVector":
        """Return a new unit PVector pointing in a random 2D direction.

        Use snake_case `random2d` per project convention.
        """
        a = random.random() * 2 * math.pi
        return cls(math.cos(a), math.sin(a))

    def dot(self, *args) -> float:
        """Dot product.

        Usage:
          v.dot(other)        # other is PVector or 2-length iterable
          v.dot(x, y)         # numeric components

        Examples
        --------
        >>> from pycreative.vector import PVector
        >>> v = PVector(10, 20)
        >>> v.dot(60, 80)
        2200.0
        >>> v.dot(PVector(60, 80))
        2200.0
        >>> # Callable as an unbound function (PVector.dot(a, b)) is supported
        >>> PVector.dot(v, PVector(60, 80))
        2200.0
        """
        if len(args) == 1:
            other = args[0]
            if isinstance(other, PVector):
                return float(self.x * other.x + self.y * other.y)
            if hasattr(other, "__iter__"):
                vals = list(other)
                if len(vals) >= 2:
                    return float(self.x * float(vals[0]) + self.y * float(vals[1]))
                raise TypeError("dot() requires a 2-length iterable when a single iterable is provided")
            raise TypeError("dot() requires a PVector or two numeric arguments")
        if len(args) == 2:
            x = float(args[0])
            y = float(args[1])
            return float(self.x * x + self.y * y)
        raise TypeError("dot() requires either one vector/iterable argument or two numeric components")

    # Note: keep a single flexible `dot(self, *args)` implementation above.
    # It can be called either as an instance method `v.dot(other)` or as
    # an unbound function via `PVector.dot(a, b)` (Python will pass `a` as
    # the first parameter when called that way).
