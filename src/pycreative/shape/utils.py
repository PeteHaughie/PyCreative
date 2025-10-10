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

    # Also consider direct attributes (fill, stroke, stroke-width)
    # SVG default fill is black when not specified and not 'none'
    fattr = elem.get('fill')
    if fattr is not None:
        fv = fattr.strip()
        if fv != 'none':
            # hex
            if fv.startswith('#') and len(fv) >= 7:
                try:
                    shape.fill = (int(fv[1:3], 16), int(fv[3:5], 16), int(fv[5:7], 16))
                except Exception:
                    pass
            # rgb(r,g,b)
            elif fv.startswith('rgb'):
                nums = [int(x) for x in re.findall(r"\d+", fv)]
                if len(nums) >= 3:
                    shape.fill = (nums[0], nums[1], nums[2])
    else:
        # if no explicit fill attr or style, SVG default is black. Only set if shape.fill not already set
        if getattr(shape, 'fill', None) is None:
            shape.fill = (0, 0, 0)

    sattr = elem.get('stroke')
    if sattr is not None:
        sv = sattr.strip()
        if sv != 'none':
            if sv.startswith('#') and len(sv) >= 7:
                try:
                    shape.stroke = (int(sv[1:3], 16), int(sv[3:5], 16), int(sv[5:7], 16))
                except Exception:
                    pass
            elif sv.startswith('rgb'):
                nums = [int(x) for x in re.findall(r"\d+", sv)]
                if len(nums) >= 3:
                    shape.stroke = (nums[0], nums[1], nums[2])

    sw = elem.get('stroke-width')
    if sw is not None:
        try:
            shape.stroke_weight = int(float(sw))
        except Exception:
            pass

    # stroke-linecap, stroke-linejoin, stroke-miterlimit, stroke-dasharray
    slc = elem.get('stroke-linecap')
    if slc is not None:
        try:
            shape.stroke_linecap = slc.strip()
        except Exception:
            pass

    slj = elem.get('stroke-linejoin')
    if slj is not None:
        try:
            shape.stroke_linejoin = slj.strip()
        except Exception:
            pass

    sm = elem.get('stroke-miterlimit')
    if sm is not None:
        try:
            shape.stroke_miterlimit = float(sm)
        except Exception:
            pass

    sda = elem.get('stroke-dasharray')
    if sda is not None:
        try:
            # numbers separated by commas or spaces
            nums = [float(x) for x in re.findall(r"[+-]?(?:\d*\.\d+|\d+)(?:[eE][+-]?\d+)?", sda)]
            shape.stroke_dasharray = nums if nums else None
        except Exception:
            pass

    fr = elem.get('fill-rule')
    if fr is not None:
        try:
            shape.fill_rule = fr.strip()
        except Exception:
            pass
