from __future__ import annotations

from typing import Tuple, Optional, Union
import pycreative

# Simple numeric alias used throughout the codebase
Number = float | int

# Color-related aliases
RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]
# ColorLike covers common input shapes accepted by the API: a single grayscale
# numeric value (e.g., 255), a 3- or 4-tuple, or the runtime
# `pycreative.color.Color` instance (referenced lazily to avoid import-time
# dependencies).
ColorLike = Union[Number, RGB, RGBA, "pycreative.color.Color"]
ColorOrNone = Optional[ColorLike]

# Geometry helpers
Matrix = list[list[float]]
Point = Tuple[float, float]

__all__ = [
    "Number",
    "RGB",
    "RGBA",
    "ColorLike",
    "ColorOrNone",
    "Matrix",
    "Point",
]
