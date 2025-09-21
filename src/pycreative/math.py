"""
pycreative.math: Utility math functions and classes for creative coding.
"""

import math
import random

# Math constants and trigonometric functions
pi = math.pi
tau = math.tau if hasattr(math, "tau") else 2 * math.pi
e = math.e


def sin(x: float) -> float:
    return math.sin(x)


def cos(x: float) -> float:
    return math.cos(x)


def tan(x: float) -> float:
    return math.tan(x)


# Utility math functions


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between a and b by t (0..1).
    """
    return a + (b - a) * t


def clamp(val: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min_val and max_val.
    """
    return max(min_val, min(max_val, val))


def map_range(
    value: float, in_min: float, in_max: float, out_min: float, out_max: float
) -> float:
    """
    Map value from one range to another.
    """
    return out_min + (out_max - out_min) * ((value - in_min) / (in_max - in_min))


# Random utilities


def random_float(a: float = 0.0, b: float = 1.0) -> float:
    """
    Return a random float in [a, b).
    """
    return random.uniform(a, b)


def random_int(a: int, b: int) -> int:
    """
    Return a random integer in [a, b].
    """
    return random.randint(a, b)


def random_seed(seed: int):
    """
    Set the random seed for reproducible results.
    """
    random.seed(seed)
