from __future__ import annotations

from typing import Tuple, Optional, Union
import pycreative

# Simple numeric alias used throughout the codebase
Number = float | int

# Color-related aliases
RGB = Tuple[int, int, int]
RGBA = Tuple[int, int, int, int]
# ColorInput covers the loose forms accepted by public APIs: a single
# grayscale numeric value (e.g., 255), a 3- or 4-tuple, or a runtime
# `pycreative.color.Color` instance. This type is intentionally permissive
# because public-facing helpers accept many shorthand forms.
ColorInput = Union[Number, RGB, RGBA, "pycreative.color.Color"]

# ColorTuple is the normalized, internal representation used by the Surface
# implementation and pygame: a concrete 3- or 4-length tuple of ints.
ColorTuple = Union[RGB, RGBA]

# Convenience Optional unions
ColorOrNone = Optional[ColorInput]
ColorTupleOrNone = Optional[ColorTuple]

# Geometry helpers
Matrix = list[list[float]]
Point = Tuple[float, float]

__all__ = [
    "Number",
    "RGB",
    "RGBA",
    "ColorInput",
    "ColorOrNone",
    "ColorTuple",
    "ColorTupleOrNone",
    "Matrix",
    "Point",
]
