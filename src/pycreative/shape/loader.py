from __future__ import annotations

from typing import List, Tuple, Optional
import xml.etree.ElementTree as ET
import re
import math

from .core import PShape
from .utils import parse_transform, apply_matrix_point, parse_style


def _parse_points_attr(s: str) -> List[Tuple[float, float]]:
    parts = s.replace(',', ' ').split()
    it = iter(parts)
    out: List[Tuple[float, float]] = []
    for a, b in zip(it, it):
        try:
            out.append((float(a), float(b)))
        except Exception:
            continue
    return out


def load_svg(path: str) -> Optional[PShape]:
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception:
        return None

    svg_ns = ''
    if root.tag.startswith('{'):
        svg_ns = root.tag.split('}')[0] + '}'

    shape = PShape()

    # viewBox
    try:
        vb = root.get('viewBox') or root.get('viewbox')
        if vb:
            nums = re.findall(r"[+-]?(?:\d*\.\d+|\d+)(?:[eE][+-]?\d+)?", vb)
            if len(nums) >= 4:
                try:
                    shape.view_box = (float(nums[0]), float(nums[1]), float(nums[2]), float(nums[3]))
                except Exception:
                    pass
    except Exception:
        pass

    def process_element(elem: ET.Element, cur_mat) -> None:
        tag = elem.tag
        if svg_ns:
            if not tag.startswith(svg_ns):
                return
            ttag = tag[len(svg_ns):]
        else:
            ttag = tag

        tattr = elem.get('transform')
        if tattr:
            mat = parse_transform(tattr)
            # compose
            cur_mat = (parse_transform('matrix(1 0 0 1 0 0)') if cur_mat is None else cur_mat)
            a1, b1, c1, d1, e1, f1 = cur_mat
            a2, b2, c2, d2, e2, f2 = mat
            # multiply m1 * m2
            composed = (a2 * a1 + c2 * b1, b2 * a1 + d2 * b1, a2 * c1 + c2 * d1, b2 * c1 + d2 * d1, a2 * e1 + c2 * f1 + e2, b2 * e1 + d2 * f1 + f2)
            cur_mat = composed

        parse_style(elem, shape)

        if ttag in ('polygon', 'polyline'):
            pts_attr = elem.get('points') or ''
            pts = _parse_points_attr(pts_attr)
            pts = [apply_matrix_point(cur_mat, px, py) for px, py in pts]
            if ttag == 'polygon' and pts and pts[0] != pts[-1]:
                pts.append(pts[0])
            shape.add_subpath(pts)
        elif ttag == 'rect':
            try:
                x = float(elem.get('x') or 0)
                y = float(elem.get('y') or 0)
                w = float(elem.get('width') or 0)
                h = float(elem.get('height') or 0)
                pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
                pts = [apply_matrix_point(cur_mat, px, py) for px, py in pts]
                shape.add_subpath(pts)
            except Exception:
                pass
        elif ttag == 'circle':
            try:
                cx = float(elem.get('cx') or 0)
                cy = float(elem.get('cy') or 0)
                r = float(elem.get('r') or 0)
                pts = []
                for k in range(24):
                    t = (k / 24.0) * 2 * math.pi
                    pts.append((cx + math.cos(t) * r, cy + math.sin(t) * r))
                pts.append(pts[0])
                pts = [apply_matrix_point(cur_mat, px, py) for px, py in pts]
                shape.add_subpath(pts)
            except Exception:
                pass
        elif ttag == 'path':
            d = elem.get('d') or ''
            num_re = r"[+-]?(?:\d*\.\d+|\d+)(?:[eE][+-]?\d+)?"
            tokens = re.findall(rf"[A-Za-z]|{num_re}", d)
            path_pts: List[Tuple[float, float]] = []
            cmd = None
            i = 0
            cur_x = 0.0
            cur_y = 0.0
            start_x = None
            prev_cx = None
            prev_cy = None
            while i < len(tokens):
                tk = tokens[i]
                if tk.isalpha():
                    cmd = tk
                    i += 1
                    continue
                if cmd is None:
                    i += 1
                    continue

                if cmd in ('M', 'L'):
                    try:
                        x = float(tokens[i])
                        y = float(tokens[i + 1])
                        cur_x, cur_y = x, y
                        if start_x is None:
                            start_x = cur_x
                        path_pts.append((cur_x, cur_y))
                        i += 2
                    except Exception:
                        i += 1
                        continue
                elif cmd in ('m', 'l'):
                    try:
                        dx = float(tokens[i])
                        dy = float(tokens[i + 1])
                        cur_x += dx
                        cur_y += dy
                        if start_x is None:
                            start_x = cur_x
                        path_pts.append((cur_x, cur_y))
                        i += 2
                    except Exception:
                        i += 1
                        continue
                elif cmd in ('C', 'c', 'S', 's'):
                    try:
                        while i + 5 < len(tokens) and not tokens[i].isalpha():
                            if cmd in ('C', 'S'):
                                cx1 = float(tokens[i])
                                cy1 = float(tokens[i + 1])
                                cx2 = float(tokens[i + 2])
                                cy2 = float(tokens[i + 3])
                                x = float(tokens[i + 4])
                                y = float(tokens[i + 5])
                            else:
                                rc1x = float(tokens[i])
                                rc1y = float(tokens[i + 1])
                                rc2x = float(tokens[i + 2])
                                rc2y = float(tokens[i + 3])
                                rx = float(tokens[i + 4])
                                ry = float(tokens[i + 5])
                                cx1 = cur_x + rc1x
                                cy1 = cur_y + rc1y
                                cx2 = cur_x + rc2x
                                cy2 = cur_y + rc2y
                                x = cur_x + rx
                                y = cur_y + ry
                            from ..shape_math import flatten_cubic_bezier

                            seg = flatten_cubic_bezier((cur_x, cur_y), (cx1, cy1), (cx2, cy2), (x, y), steps=20)
                            if seg:
                                for p in seg[1:]:
                                    path_pts.append(p)
                            prev_cx, prev_cy = cx2, cy2
                            cur_x, cur_y = x, y
                            i += 6
                    except Exception:
                        i += 1
                        continue
                elif cmd in ('Q', 'q', 'T', 't'):
                    try:
                        while i + 1 < len(tokens) and not tokens[i].isalpha():
                            if cmd in ('Q', 'q'):
                                if cmd == 'Q':
                                    qx1 = float(tokens[i])
                                    qy1 = float(tokens[i + 1])
                                    x = float(tokens[i + 2])
                                    y = float(tokens[i + 3])
                                    i_step = 4
                                else:
                                    rqx1 = float(tokens[i])
                                    rqy1 = float(tokens[i + 1])
                                    qx1 = cur_x + rqx1
                                    qy1 = cur_y + rqy1
                                    x = cur_x + float(tokens[i + 2])
                                    y = cur_y + float(tokens[i + 3])
                                    i_step = 4
                            else:
                                if prev_cx is not None and prev_cy is not None:
                                    qx1 = 2 * cur_x - prev_cx
                                    qy1 = 2 * cur_y - prev_cy
                                else:
                                    qx1 = cur_x
                                    qy1 = cur_y
                                if cmd == 'T':
                                    x = float(tokens[i])
                                    y = float(tokens[i + 1])
                                else:
                                    x = cur_x + float(tokens[i])
                                    y = cur_y + float(tokens[i + 1])
                                i_step = 2
                            from ..shape_math import flatten_quadratic_bezier

                            seg = flatten_quadratic_bezier((cur_x, cur_y), (qx1, qy1), (x, y), steps=16)
                            if seg:
                                for p in seg[1:]:
                                    path_pts.append(p)
                            prev_cx, prev_cy = qx1, qy1
                            cur_x, cur_y = x, y
                            i += i_step
                    except Exception:
                        i += 1
                        continue
                elif cmd in ('A', 'a'):
                    try:
                        while i + 6 < len(tokens) and not tokens[i].isalpha():
                            rx = float(tokens[i])
                            ry = float(tokens[i + 1])
                            xar = float(tokens[i + 2])
                            laf = int(float(tokens[i + 3]))
                            sf = int(float(tokens[i + 4]))
                            if cmd == 'A':
                                x = float(tokens[i + 5])
                                y = float(tokens[i + 6])
                            else:
                                x = cur_x + float(tokens[i + 5])
                                y = cur_y + float(tokens[i + 6])
                            from ..shape_math import flatten_arc

                            seg = flatten_arc((cur_x, cur_y), (x, y), rx, ry, xar, laf, sf)
                            if seg:
                                for p in seg[1:]:
                                    path_pts.append(p)
                            cur_x, cur_y = x, y
                            prev_cx, prev_cy = None, None
                            i += 7
                    except Exception:
                        i += 1
                        continue
                else:
                    i += 1

            if path_pts:
                path_pts = [apply_matrix_point(cur_mat, px, py) for px, py in path_pts]
                shape.add_subpath(path_pts)

        for child in elem:
            process_element(child, cur_mat)

    identity = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    process_element(root, identity)
    return shape
