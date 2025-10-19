"""Matrix and transform helpers for the Engine.

This module provides small, mostly-pure helpers for 3x3 matrix
operations and functions that operate on an Engine instance's matrix
stack. They are extracted from the large engine implementation to keep
that file smaller and easier to reason about.
"""
from typing import Any, List, Optional


def identity_matrix() -> List[float]:
    """Return a 3x3 identity matrix as a flat list (row-major)."""
    return [1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0]


def mul_mat(a: List[float], b: List[float]) -> List[float]:
    """Multiply two 3x3 matrices (flat row-major lists).

    Returns a new flat list representing a*b.
    """
    return [
        a[0]*b[0] + a[1]*b[3] + a[2]*b[6],
        a[0]*b[1] + a[1]*b[4] + a[2]*b[7],
        a[0]*b[2] + a[1]*b[5] + a[2]*b[8],

        a[3]*b[0] + a[4]*b[3] + a[5]*b[6],
        a[3]*b[1] + a[4]*b[4] + a[5]*b[7],
        a[3]*b[2] + a[4]*b[5] + a[5]*b[8],

        a[6]*b[0] + a[7]*b[3] + a[8]*b[6],
        a[6]*b[1] + a[7]*b[4] + a[8]*b[7],
        a[6]*b[2] + a[7]*b[5] + a[8]*b[8],
    ]


def ensure_matrix_stack(engine: Any) -> None:
    if not hasattr(engine, '_matrix_stack'):
        engine._matrix_stack = [identity_matrix()]


def push_matrix(engine: Any):
    ensure_matrix_stack(engine)
    try:
        top = list(engine._matrix_stack[-1])
        engine._matrix_stack.append(top)
    except Exception:
        engine._matrix_stack = [identity_matrix()]
    try:
        return engine.graphics.record('push_matrix')
    except Exception:
        return None


def pop_matrix(engine: Any):
    ensure_matrix_stack(engine)
    try:
        if len(engine._matrix_stack) > 1:
            engine._matrix_stack.pop()
        else:
            engine._matrix_stack[-1] = identity_matrix()
    except Exception:
        engine._matrix_stack = [identity_matrix()]
    try:
        return engine.graphics.record('pop_matrix')
    except Exception:
        return None


def reset_matrix(engine: Any):
    ensure_matrix_stack(engine)
    try:
        engine._matrix_stack[-1] = identity_matrix()
    except Exception:
        engine._matrix_stack = [identity_matrix()]
    try:
        return engine.graphics.record('reset_matrix')
    except Exception:
        return None


def apply_transform_matrix(engine: Any, mat: List[float]) -> None:
    """Right-multiply the current matrix by mat (both flat 3x3 lists)."""
    ensure_matrix_stack(engine)
    try:
        cur = engine._matrix_stack[-1]
        engine._matrix_stack[-1] = mul_mat(cur, mat)
    except Exception:
        engine._matrix_stack[-1] = list(mat)


def translate(engine: Any, x: float, y: float):
    try:
        tx = float(x)
        ty = float(y)
    except Exception:
        return None
    mat = [1.0, 0.0, tx,
           0.0, 1.0, ty,
           0.0, 0.0, 1.0]
    apply_transform_matrix(engine, mat)
    try:
        return engine.graphics.record('translate', x=tx, y=ty)
    except Exception:
        return None


def rotate(engine: Any, angle: float):
    import math
    try:
        a = float(angle)
    except Exception:
        return None
    c = math.cos(a)
    s = math.sin(a)
    mat = [c, -s, 0.0,
           s,  c, 0.0,
           0.0,0.0,1.0]
    apply_transform_matrix(engine, mat)
    try:
        return engine.graphics.record('rotate', angle=float(a))
    except Exception:
        return None


def scale(engine: Any, sx: float, sy: Optional[float] = None):
    try:
        sx_f = float(sx)
        sy_f = float(sy) if sy is not None else sx_f
    except Exception:
        return None
    mat = [sx_f, 0.0, 0.0,
           0.0, sy_f, 0.0,
           0.0, 0.0, 1.0]
    apply_transform_matrix(engine, mat)
    try:
        return engine.graphics.record('scale', sx=sx_f, sy=sy_f)
    except Exception:
        return None


def shear_x(engine: Any, angle: float):
    import math
    try:
        a = float(angle)
    except Exception:
        return None
    mat = [1.0, math.tan(a), 0.0,
           0.0, 1.0,        0.0,
           0.0, 0.0,        1.0]
    apply_transform_matrix(engine, mat)
    try:
        return engine.graphics.record('shear_x', angle=float(a))
    except Exception:
        return None


def shear_y(engine: Any, angle: float):
    import math
    try:
        a = float(angle)
    except Exception:
        return None
    mat = [1.0, 0.0,        0.0,
           math.tan(a), 1.0, 0.0,
           0.0, 0.0,        1.0]
    apply_transform_matrix(engine, mat)
    try:
        return engine.graphics.record('shear_y', angle=float(a))
    except Exception:
        return None


def apply_matrix(engine: Any, *args):
    """Apply a provided matrix to the current transform.

    Accepts either a single sequence-like of 9 or 6 numbers, or 6/9 numbers
    as individual arguments. For 6 numbers we expand them into a 3x3
    affine matrix with a bottom row [0,0,1].
    """
    vals = None
    if len(args) == 1:
        maybe = args[0]
        try:
            vals = list(maybe)
        except Exception:
            vals = None
    else:
        vals = list(args)

    if vals is None:
        return None

    try:
        if len(vals) == 6:
            mat = [float(vals[0]), float(vals[1]), float(vals[2]),
                   float(vals[3]), float(vals[4]), float(vals[5]),
                   0.0, 0.0, 1.0]
            apply_transform_matrix(engine, mat)
        elif len(vals) == 9:
            mat = [float(v) for v in vals]
            apply_transform_matrix(engine, mat)
        elif len(vals) == 16:
            mat = [float(v) for v in vals]
            # For 4x4 inputs we don't modify the 3x3 stack; just record.
        else:
            return None
    except Exception:
        return None

    try:
        return engine.graphics.record('apply_matrix', matrix=mat)
    except Exception:
        return None
