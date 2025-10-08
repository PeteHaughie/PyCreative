from __future__ import annotations

import math
import re
from xml.etree import ElementTree as ET


def _mul_matrix(m1, m2):
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    a = a2 * a1 + c2 * b1
    b = b2 * a1 + d2 * b1
    c = a2 * c1 + c2 * d1
    d = b2 * c1 + d2 * d1
    e = a2 * e1 + c2 * f1 + e2
    f = b2 * e1 + d2 * f1 + f2
    return (a, b, c, d, e, f)


def parse_transform(transform: str):
    if not transform:
        return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    mat = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    token_re = re.compile(r"([a-zA-Z]+)\s*\(([^)]*)\)")
    for m in token_re.finditer(transform):
        name = m.group(1)
        args = [float(x) for x in re.findall(r"[+-]?(?:\d*\.\d+|\d+)(?:[eE][+-]?\d+)?", m.group(2))]
        if name == 'translate':
            tx = args[0] if len(args) > 0 else 0.0
            ty = args[1] if len(args) > 1 else 0.0
            t = (1.0, 0.0, 0.0, 1.0, tx, ty)
        elif name == 'scale':
            sx = args[0] if len(args) > 0 else 1.0
            sy = args[1] if len(args) > 1 else sx
            t = (sx, 0.0, 0.0, sy, 0.0, 0.0)
        elif name == 'rotate':
            a = args[0] if len(args) > 0 else 0.0
            rad = math.radians(a)
            ca = math.cos(rad)
            sa = math.sin(rad)
            if len(args) >= 3:
                cx = args[1]
                cy = args[2]
                t = (ca, sa, -sa, ca, cx - ca * cx + sa * cy, cy - sa * cx - ca * cy)
            else:
                t = (ca, sa, -sa, ca, 0.0, 0.0)
        elif name == 'matrix':
            if len(args) >= 6:
                t = (args[0], args[1], args[2], args[3], args[4], args[5])
            else:
                t = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        else:
            t = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        mat = _mul_matrix(mat, t)
    return mat


def apply_matrix_point(mat, x: float, y: float):
    a, b, c, d, e, f = mat
    nx = a * x + c * y + e
    ny = b * x + d * y + f
    return (nx, ny)


def parse_style(elem: ET.Element, shape) -> None:
    style = elem.get('style') or ''
    for p in [x.strip() for x in style.split(';') if x.strip()]:
        if ':' not in p:
            continue
        k, v = p.split(':', 1)
        k = k.strip()
        v = v.strip()
        if k == 'fill' and v != 'none' and v.startswith('#') and len(v) >= 7:
            try:
                shape.fill = (int(v[1:3], 16), int(v[3:5], 16), int(v[5:7], 16))
            except Exception:
                pass
        if k == 'stroke' and v != 'none' and v.startswith('#') and len(v) >= 7:
            try:
                shape.stroke = (int(v[1:3], 16), int(v[3:5], 16), int(v[5:7], 16))
            except Exception:
                pass
        if k == 'stroke-width':
            try:
                shape.stroke_weight = int(float(v))
            except Exception:
                pass
