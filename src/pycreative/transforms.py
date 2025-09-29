"""Small 2D affine transform helpers.

This module provides lightweight, numpy-free helpers for 3x3 homogeneous 2D
affine transforms. The representation is a nested list (3x3) of floats where
the last row is always [0,0,1]. Functions are intentionally small and
dependency-free so they can be used in tests and headless environments.

Matrix multiplication order used here follows the convention:
    result = multiply(A, B)
represents the transform that applies A then B to points (i.e. right-multiplication
of column vectors when using homogeneous coordinates). In the Surface API we
apply new operations by multiplying the current matrix by the operation matrix
using this helper (current = multiply(current, op)).

Public helpers:
- identity_matrix()
- multiply(A, B)
- translate_matrix(dx, dy)
- rotate_matrix(theta)  # theta in radians
- scale_matrix(sx, sy)
- transform_point(M, x, y) -> (x', y')
- transform_points(M, iterable_of_points) -> list[(x', y')]
- decompose_scale(M) -> (sx, sy)  # approximate scale factors from linear part
"""
from __future__ import annotations

from math import cos, sin, hypot
from typing import Iterable, List, Sequence, Tuple

Matrix = List[List[float]]


def identity_matrix() -> Matrix:
    """Return a 3x3 identity matrix.

    The matrix is in row-major order and the last row is always [0,0,1].
    """
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]


def multiply(A: Matrix, B: Matrix) -> Matrix:
    """Multiply two 3x3 matrices (A @ B) and return the result.

    This implements standard row-major matrix multiplication.
    """
    return [
        [
            A[0][0] * B[0][0] + A[0][1] * B[1][0] + A[0][2] * B[2][0],
            A[0][0] * B[0][1] + A[0][1] * B[1][1] + A[0][2] * B[2][1],
            A[0][0] * B[0][2] + A[0][1] * B[1][2] + A[0][2] * B[2][2],
        ],
        [
            A[1][0] * B[0][0] + A[1][1] * B[1][0] + A[1][2] * B[2][0],
            A[1][0] * B[0][1] + A[1][1] * B[1][1] + A[1][2] * B[2][1],
            A[1][0] * B[0][2] + A[1][1] * B[1][2] + A[1][2] * B[2][2],
        ],
        [0.0, 0.0, 1.0],
    ]


def translate_matrix(dx: float, dy: float) -> Matrix:
    """Return a translation matrix that translates by (dx, dy)."""
    return [[1.0, 0.0, dx], [0.0, 1.0, dy], [0.0, 0.0, 1.0]]


def rotate_matrix(theta: float) -> Matrix:
    """Return a rotation matrix for angle theta (radians)."""
    c = cos(theta)
    s = sin(theta)
    return [[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]


def scale_matrix(sx: float, sy: float | None = None) -> Matrix:
    """Return a scaling matrix. If sy is None, uniform scale is used."""
    if sy is None:
        sy = sx
    return [[float(sx), 0.0, 0.0], [0.0, float(sy), 0.0], [0.0, 0.0, 1.0]]


def transform_point(M: Matrix, x: float, y: float) -> Tuple[float, float]:
    """Apply 3x3 matrix M to point (x, y) and return transformed (x', y')."""
    tx = M[0][0] * x + M[0][1] * y + M[0][2]
    ty = M[1][0] * x + M[1][1] * y + M[1][2]
    return (tx, ty)


def transform_points(M: Matrix, pts: Iterable[Sequence[float]]) -> List[Tuple[float, float]]:
    """Apply matrix M to an iterable of (x,y) points and return a new list."""
    return [transform_point(M, float(x), float(y)) for (x, y) in pts]


def decompose_scale(M: Matrix) -> Tuple[float, float]:
    """Estimate scale factors (sx, sy) from the linear part of M.

    This computes the Euclidean norm of the first and second column vectors of
    the 2x2 linear submatrix [[a,b],[d,e]] which corresponds to the x and y
    scale factors when there is no shear. It is a sensible heuristic to use
    when adjusting stroke widths under non-uniform transforms.
    """
    # Columns: (a, d) and (b, e)
    a = M[0][0]
    b = M[0][1]
    d = M[1][0]
    e = M[1][1]
    sx = hypot(a, d)
    sy = hypot(b, e)
    return (sx, sy)


def linear_determinant(M: Matrix) -> float:
    """Return determinant of the linear (2x2) part of the 3x3 matrix M."""
    return M[0][0] * M[1][1] - M[0][1] * M[1][0]
