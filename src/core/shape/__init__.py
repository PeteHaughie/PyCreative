"""Shape API package.

This package is a thin re-export of implementations in `primitives` and
`path` to keep import-time costs low and make the implementation easy to
test and refactor.
"""
from .primitives import (  # noqa: F401
    rect,
    line,
    square,
    circle,
    ellipse,
    point,
    stroke_weight,
)
from .path import begin_shape, vertex, end_shape  # noqa: F401

__all__ = [
    # primitives
    'rect',
    'line',
    'square',
    'circle',
    'ellipse',
    'point',
    'stroke_weight',
    # path
    'begin_shape',
    'vertex',
    'end_shape',
]
