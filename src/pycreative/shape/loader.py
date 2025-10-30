"""SVG loader (vector-only) for PyCreative.

This module provides a conservative XML-based SVG loader that converts
vector primitives into skia.Path objects. It intentionally avoids any
raster fallbacks.

Features:
- parse <circle>, <rect>, <ellipse>, <polygon>, <polyline>, <path>
- handle transform lists (translate, scale, rotate, skewX, skewY, matrix)
- basic style parsing for fill / stroke and opacities (hex and rgb(a))

The implementation favors robustness over fidelity (paths are approximated
when necessary) so it remains pure-vector and import-safe.
"""

from __future__ import annotations

import math
import os
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

try:
    import skia
except Exception:  # pragma: no cover - skia should be available in runtime
    skia = None  # type: ignore

# Lightweight fallback Path/Rect classes used when skia is not available so
# the loader still returns vector-like objects that tests can inspect.
if skia is None:
    class _FakeRect:
        def __init__(self, left=0, top=0, right=0, bottom=0):
            self._l = left
            self._t = top
            self._r = right
            self._b = bottom

        def left(self):
            return self._l

        def top(self):
            return self._t

        def right(self):
            return self._r

        def bottom(self):
            return self._b

    class _FakePath:
        def __init__(self):
            self._pts: List[Tuple[float, float]] = []

        def moveTo(self, x, y):
            self._pts.append((x, y))

        def lineTo(self, x, y):
            self._pts.append((x, y))

        def close(self):
            pass

        def addCircle(self, cx, cy, r):
            # approximate circle bounding box
            self._pts.append((cx - r, cy - r))
            self._pts.append((cx + r, cy + r))

        def addRect(self, rect):
            try:
                l = rect.left()
                t = rect.top()
                r = rect.right()
                b = rect.bottom()
                self._pts.append((l, t))
                self._pts.append((r, b))
            except Exception:
                pass

        def addOval(self, rect):
            self.addRect(rect)

        def addRoundRect(self, rect, rx, ry):
            self.addRect(rect)

        def transform(self, *args, **kwargs):
            # no-op for fallback
            return

        def computeTightBounds(self):
            if not self._pts:
                return _FakeRect(0, 0, 0, 0)
            xs = [p[0] for p in self._pts]
            ys = [p[1] for p in self._pts]
            return _FakeRect(min(xs), min(ys), max(xs), max(ys))

    # expose fake classes under the skia name used by the rest of the file
    class _MatrixStub:
        @staticmethod
        def MakeAll(a, b, c, d, e, f):
            return (a, b, c, d, e, f)

    class _skia_stub:
        Path = _FakePath
        Rect = _FakeRect
        Matrix = _MatrixStub

    skia = _skia_stub()

try:
    from svg.path import parse_path
except Exception:  # pragma: no cover - tests supply svg.path
    parse_path = None  # type: ignore


def _ensure_file(path: str) -> str:
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return path


class PCShape:
    def __init__(self):
        self.skia_paths: List[skia.Path] = [] if skia else []
        self.paths: List[Dict[str, Any]] = []


def _parse_number(v: Optional[str], default: float = 0.0) -> float:
    if v is None:
        return default
    try:
        return float(v)
    except Exception:
        # strip units like px
        try:
            return float(re.sub(r"[a-zA-Z%]+$", "", v))
        except Exception:
            return default


def _parse_color(s: Optional[str]) -> Optional[Tuple[float, float, float, float]]:
    if not s:
        return None
    s = s.strip()
    # hex
    m = re.match(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", s)
    if m:
        hexs = m.group(1)
        if len(hexs) == 3:
            r = int(hexs[0] * 2, 16)
            g = int(hexs[1] * 2, 16)
            b = int(hexs[2] * 2, 16)
        else:
            r = int(hexs[0:2], 16)
            g = int(hexs[2:4], 16)
            b = int(hexs[4:6], 16)
        return (r / 255.0, g / 255.0, b / 255.0, 1.0)
    # rgb/rgba
    m = re.match(r"rgba?\(([^)]+)\)", s)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        if len(parts) >= 3:
            try:
                r = float(parts[0])
                g = float(parts[1])
                b = float(parts[2])
                a = float(parts[3]) if len(parts) > 3 else 1.0
                if r > 1 or g > 1 or b > 1:
                    r /= 255.0
                    g /= 255.0
                    b /= 255.0
                return (r, g, b, a)
            except Exception:
                return None
    # basic named colors (small set)
    NAMED = {
        "black": (0, 0, 0, 1),
        "white": (1, 1, 1, 1),
        "red": (1, 0, 0, 1),
        "green": (0, 1, 0, 1),
        "blue": (0, 0, 1, 1),
        "none": None,
    }
    key = s.lower()
    return NAMED.get(key)


def _compose_matrix(m1: Tuple[float, float, float, float, float, float],
                    m2: Tuple[float, float, float, float, float, float]) -> Tuple[float, float, float, float, float, float]:
    # Multiply 3x3 matrices in SVG layout. Matrices are (a,b,c,d,e,f):
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    a = a1 * a2 + c1 * b2
    b = b1 * a2 + d1 * b2
    c = a1 * c2 + c1 * d2
    d = b1 * c2 + d1 * d2
    e = a1 * e2 + c1 * f2 + e1
    f = b1 * e2 + d1 * f2 + f1
    return (a, b, c, d, e, f)


def parse_matrix(transform: Optional[str]) -> Tuple[float, float, float, float, float, float]:
    """Parse an SVG transform list into an (a,b,c,d,e,f) matrix.

    Supports: translate(tx,ty), scale(sx[,sy]), rotate(angle[,cx,cy]),
    skewX(angle), skewY(angle), and matrix(a,b,c,d,e,f).
    The transforms are composed in the order they appear.
    Returns a tuple suitable for skia.Matrix.MakeAll(a,b,c,d,e,f).
    """
    # identity
    mat: Tuple[float, float, float, float, float, float] = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    if not transform:
        return mat
    transform = transform.strip()
    # tokenise function calls
    for fn, args_text in re.findall(r"(\w+)\s*\(([^)]*)\)", transform):
        args = [float(re.sub(r"[a-zA-Z%]+$", "", a.strip())) for a in args_text.split(",") if a.strip()]
        fn = fn.strip()
        if fn == "translate":
            tx = args[0] if len(args) > 0 else 0.0
            ty = args[1] if len(args) > 1 else 0.0
            m = (1.0, 0.0, 0.0, 1.0, tx, ty)
        elif fn == "scale":
            sx = args[0] if len(args) > 0 else 1.0
            sy = args[1] if len(args) > 1 else sx
            m = (sx, 0.0, 0.0, sy, 0.0, 0.0)
        elif fn == "rotate":
            a = math.radians(args[0] if len(args) > 0 else 0.0)
            cos = math.cos(a)
            sin = math.sin(a)
            if len(args) > 2:
                cx = args[1]
                cy = args[2]
                # translate(cx,cy) * rotate * translate(-cx,-cy)
                m1 = (1.0, 0.0, 0.0, 1.0, cx, cy)
                mr = (cos, sin, -sin, cos, 0.0, 0.0)
                m2 = (1.0, 0.0, 0.0, 1.0, -cx, -cy)
                m = _compose_matrix(_compose_matrix(m1, mr), m2)
            else:
                m = (cos, sin, -sin, cos, 0.0, 0.0)
        elif fn == "skewX":
            a = math.radians(args[0] if len(args) > 0 else 0.0)
            m = (1.0, 0.0, math.tan(a), 1.0, 0.0, 0.0)
        elif fn == "skewY":
            a = math.radians(args[0] if len(args) > 0 else 0.0)
            m = (1.0, math.tan(a), 0.0, 1.0, 0.0, 0.0)
        elif fn == "matrix":
            if len(args) >= 6:
                m = (args[0], args[1], args[2], args[3], args[4], args[5])
            else:
                m = mat
        else:
            m = mat
        mat = _compose_matrix(mat, m)
    return mat


def _apply_matrix_to_path(path: "skia.Path", mat_components: Tuple[float, float, float, float, float, float]) -> None:
    if not skia:
        return
    a, b, c, d, e, f = mat_components
    # Different skia builds expose MakeAll with different signatures.
    # Try the common 6-arg form first; if it fails, try the 9-arg form
    # which expects (scaleX, skewX, transX, skewY, scaleY, transY, pers0, pers1, pers2).
    try:
        m = skia.Matrix.MakeAll(a, b, c, d, e, f)
    except TypeError:
        try:
            # Map SVG matrix (a,c,e; b,d,f; 0,0,1) into MakeAll params
            m = skia.Matrix.MakeAll(a, c, e, b, d, f, 0.0, 0.0, 1.0)
        except Exception:
            return
    try:
        path.transform(m)
    except Exception:
        # older skia bindings may use slightly different APIs; ignore if it fails
        pass


def _path_from_points(points: List[Tuple[float, float]], close: bool = True) -> "skia.Path":
    p = skia.Path()
    if not points:
        return p
    x0, y0 = points[0]
    p.moveTo(x0, y0)
    for x, y in points[1:]:
        p.lineTo(x, y)
    if close:
        p.close()
    return p


def _parse_path_d_to_skia(d: str) -> "skia.Path":
    # Conservative approximation: sample each segment at several t positions.
    p = skia.Path()
    if not parse_path:
        # Simple fallback: extract numeric coordinate pairs from common M/L commands.
        nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", d)
        pts: List[Tuple[float, float]] = []
        for i in range(0, len(nums) - 1, 2):
            try:
                x = float(nums[i])
                y = float(nums[i + 1])
                pts.append((x, y))
            except Exception:
                continue
        if pts:
            return _path_from_points(pts, close=d.strip().upper().endswith('Z'))
        return p
    try:
        parsed = parse_path(d)
    except Exception:
        return p
    first = True
    for seg in parsed:
        steps = 12
        try:
            for i in range(steps + 1):
                t = i / steps
                pt = seg.point(t)
                x, y = float(pt.real), float(pt.imag)
                if first:
                    p.moveTo(x, y)
                    first = False
                else:
                    p.lineTo(x, y)
        except Exception:
            # fallback: try to move/line using endpoints
            try:
                sx = float(seg.start.real)
                sy = float(seg.start.imag)
                ex = float(seg.end.real)
                ey = float(seg.end.imag)
                if first:
                    p.moveTo(sx, sy)
                    first = False
                p.lineTo(ex, ey)
            except Exception:
                continue
    return p


def _parse_style(elem: ET.Element) -> Dict[str, Any]:
    style: Dict[str, Any] = {}
    inline = elem.get("style") or ""
    # parse inline style: key:val;...
    for part in inline.split(";"):
        if not part.strip():
            continue
        if ":" in part:
            k, v = part.split(":", 1)
            style[k.strip()] = v.strip()
    # presentation attributes
    for k in ("fill", "stroke", "fill-opacity", "stroke-opacity", "opacity", "stroke-width", "stroke-linecap", "stroke-linejoin"):
        v = elem.get(k)
        if v is not None:
            style[k] = v
    # normalize color/opacity
    raw_fill = style.get("fill")
    raw_stroke = style.get("stroke")
    fill = _parse_color(raw_fill)
    stroke = _parse_color(raw_stroke)
    opacity = float(style.get("opacity", 1.0)) if style.get("opacity") is not None else 1.0

    # SVG default: fill is black unless explicitly 'none'
    if raw_fill is None:
        # default fill black
        fill = (0.0, 0.0, 0.0, 1.0)

    if fill is not None:
        fr, fg, fb, fa = fill
        fo = float(style.get("fill-opacity", fa))
        style["fill_rgba"] = (fr, fg, fb, fa * fo * opacity)
    else:
        style["fill_rgba"] = None

    # default stroke: none (keep None unless specified)
    if stroke is not None:
        sr, sg, sb, sa = stroke
        so = float(style.get("stroke-opacity", sa))
        style["stroke_rgba"] = (sr, sg, sb, sa * so * opacity)
    else:
        style["stroke_rgba"] = None
    return style


def load_svg(path: str) -> PCShape:
    """Load an SVG file (vector-only) and return a PCShape containing skia paths.

    The function is deliberately defensive: if skia or svg.path are not
    available the returned PCShape will be mostly empty but the function
    will not raise during import.
    """
    _ensure_file(path)
    text = open(path, "rb").read()
    try:
        # strip leading whitespace that can break XML declaration position
        root = ET.fromstring(text.lstrip())
    except Exception as e:
        # try decoding as text then parse
        try:
            root = ET.fromstring(text.decode("utf-8").lstrip())
        except Exception:
            raise

    shape = PCShape()

    def recurse(node: ET.Element, inherited_matrix: Tuple[float, float, float, float, float, float]):
        # compute this node's transform
        t = node.get("transform")
        local = parse_matrix(t) if t else (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        total = _compose_matrix(inherited_matrix, local)

        tag = node.tag.split("}")[-1]
        style = _parse_style(node)

        path_obj = None
        try:
            if tag == "g":
                # group: recurse into children
                for ch in node:
                    recurse(ch, total)
                return
            elif tag == "circle":
                cx = _parse_number(node.get("cx"), 0.0)
                cy = _parse_number(node.get("cy"), 0.0)
                r = _parse_number(node.get("r"), 0.0)
                p = skia.Path()
                try:
                    p.addCircle(cx, cy, r)
                except Exception:
                    # legacy API fallback
                    p.addOval(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r))
                path_obj = p
            elif tag == "rect":
                x = _parse_number(node.get("x"), 0.0)
                y = _parse_number(node.get("y"), 0.0)
                w = _parse_number(node.get("width"), 0.0)
                h = _parse_number(node.get("height"), 0.0)
                rx = _parse_number(node.get("rx"), 0.0)
                ry = _parse_number(node.get("ry"), rx)
                p = skia.Path()
                if rx > 0 or ry > 0:
                    try:
                        p.addRoundRect(skia.Rect.MakeLTRB(x, y, x + w, y + h), rx, ry)
                    except Exception:
                        p.addRect(skia.Rect.MakeLTRB(x, y, x + w, y + h))
                else:
                    p.addRect(skia.Rect.MakeLTRB(x, y, x + w, y + h))
                path_obj = p
            elif tag == "ellipse":
                cx = _parse_number(node.get("cx"), 0.0)
                cy = _parse_number(node.get("cy"), 0.0)
                rx = _parse_number(node.get("rx"), 0.0)
                ry = _parse_number(node.get("ry"), 0.0)
                p = skia.Path()
                p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
                path_obj = p
            elif tag in ("polygon", "polyline"):
                pts = (node.get("points") or "").strip()
                coords = [c for c in re.split(r"[\s,]+", pts) if c]
                points = []
                for i in range(0, len(coords), 2):
                    try:
                        x = float(coords[i])
                        y = float(coords[i + 1])
                        points.append((x, y))
                    except Exception:
                        continue
                close = tag == "polygon"
                path_obj = _path_from_points(points, close=close)
            elif tag == "path":
                d = node.get("d") or ""
                path_obj = _parse_path_d_to_skia(d)
            else:
                # unsupported element: recurse children
                for ch in node:
                    recurse(ch, total)
                return
        except Exception:
            path_obj = None

        if path_obj is not None:
            _apply_matrix_to_path(path_obj, total)
            shape.skia_paths.append(path_obj)
            shape.paths.append({"style": style, "tag": tag})

        # recurse children for nested shapes
        for ch in node:
            recurse(ch, total)

    recurse(root, (1.0, 0.0, 0.0, 1.0, 0.0, 0.0))
    return shape


# compatibility alias expected by package exports
def load_shape(path: str) -> PCShape:
    """Compatibility wrapper used by package-level imports.

    Historically callers used `load_shape`; keep that alias to avoid
    import errors.
    """
    return load_svg(path)

