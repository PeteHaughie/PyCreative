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
from typing import Any, Dict, List, Optional, Tuple, Callable

# Import skia if available; fallback to None without a prior annotation to
# avoid a mypy "redefinition" complaint when the import succeeds.
try:
    import skia
except Exception:  # pragma: no cover - skia should be available in runtime
    skia = None

# Lightweight fallback Path/Rect classes used when skia is not available so
# the loader still returns vector-like objects that tests can inspect.
if skia is None:
    class _FakeRect:
        def __init__(self, left=0, top=0, right=0, bottom=0):
            self._l = left
            self._t = top
            self._r = right
            self._b = bottom

        @staticmethod
        def MakeLTRB(left, top, right, bottom):
            return _FakeRect(left, top, right, bottom)

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
                left = rect.left()
                top = rect.top()
                right = rect.right()
                bottom = rect.bottom()
                self._pts.append((left, top))
                self._pts.append((right, bottom))
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

# Optional svg.path.parse_path helper. Annotate as an optional callable so mypy
# understands the name even when the optional dependency is missing.
parse_path: Optional[Callable[..., Any]] = None
try:
    from svg.path import parse_path as _parse_path
    parse_path = _parse_path
except Exception:
    parse_path = None


def _ensure_file(path: str) -> str:
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return path


class PCShape:
    """Lightweight PCShape-like object returned by the SVG loader.

    The full Processing-style PCShape API is large; the SVG loader returns a
    minimal, compatible object that exposes `skia_paths` and `paths` and a few
    small helper methods/properties that callers expect (width/height and
    no-op style/transform helpers). This keeps loader-returned shapes usable
    by the rest of the codebase without requiring a heavy PCShape class.
    """

    def __init__(self):
        # list of skia.Path-like objects created by the loader
        self.skia_paths: List[skia.Path] = [] if skia else []
        # per-path metadata (style/tag) collected during parsing
        # each entry is typically {'style': {...}, 'tag': 'path'}
        self.paths: List[Dict[str, Any]] = []
        # document-level width/height (floats) when available from <svg>
        self.width: Optional[float] = None
        self.height: Optional[float] = None

        # Visibility and style flags
        self._visible: bool = True
        self._use_style: bool = True

        # Children: for compatibility we can treat each appended child as
        # a nested PCShape. The loader itself doesn't currently create
        # explicit group children, but callers may programmatically add
        # children.
        self._children: List["PCShape"] = []

        # For programmatic shape creation (create_shape / begin_shape), we
        # store transient recording state here. Recorded commands are kept
        # in path_cmds entries inside self.paths for later inspection.
        self._building: bool = False
        self._current_cmds: List[Dict[str, Any]] = []
        self._current_closed: bool = False

        # Simple transform storage (not applied eagerly to skia_paths).
        # Callers may query/expect transform methods to exist — we record
        # transforms but don't mutate existing path geometry here.
        self._tx: float = 0.0
        self._ty: float = 0.0
        self._sx: float = 1.0
        self._sy: float = 1.0
        self._rotation: float = 0.0

    # Visibility
    def is_visible(self) -> bool:
        return bool(self._visible)

    def set_visible(self, v: bool):
        try:
            self._visible = bool(v)
        except Exception:
            self._visible = True
        return None

    # Style helpers
    def enable_style(self):
        self._use_style = True
        return None

    def disable_style(self):
        self._use_style = False
        return None

    # Child management
    def add_child(self, who: "PCShape") -> "PCShape":
        if not isinstance(who, PCShape):
            raise TypeError('add_child expects a PCShape')
        self._children.append(who)
        return who

    def get_child_count(self) -> int:
        return len(self._children)

    def get_child(self, index: int) -> Optional["PCShape"]:
        try:
            return self._children[int(index)]
        except Exception:
            return None

    # Simple programmatic shape recording (begin_shape / vertex / end_shape)
    def begin_shape(self, kind: Optional[str] = None):
        self._building = True
        self._current_cmds = []
        self._current_closed = False
        return None

    def end_shape(self, close: bool = False):
        if not self._building:
            return None
        self._building = False
        self._current_closed = bool(close)
        # Convert recorded commands into a skia.Path if available
        cmds = list(self._current_cmds)
        # store in paths for fallback rendering
        self.paths.append({'path_cmds': cmds, 'style': {}})
        try:
            if skia:
                p = skia.Path()
                first = True
                for cmd in cmds:
                    c = cmd.get('cmd')
                    if c in ('moveTo', 'lineTo'):
                        for (x, y) in cmd.get('pts', []):
                            if first and c == 'moveTo':
                                p.moveTo(float(x), float(y))
                                first = False
                            else:
                                p.lineTo(float(x), float(y))
                    elif c == 'close':
                        p.close()
                if self._current_closed:
                    p.close()
                self.skia_paths.append(p)
        except Exception:
            # leave only the path_cmds if skia conversion failed
            pass
        self._current_cmds = []
        return None

    def begin_contour(self):
        # For simplicity, a contour is just another sequence of cmds
        # represented inside the current path_cmds.
        return None

    def end_contour(self):
        return None

    def get_vertex_count(self) -> int:
        # Count vertices recorded in path_cmds across all stored paths
        total = 0
        for p in self.paths:
            cmds = p.get('path_cmds') or []
            for c in cmds:
                if c.get('cmd') in ('moveTo', 'lineTo'):
                    total += len(c.get('pts', []))
        return total

    def get_vertex(self, index: int) -> Optional[Tuple[float, float]]:
        i = int(index)
        cnt = 0
        for p in self.paths:
            cmds = p.get('path_cmds') or []
            for c in cmds:
                if c.get('cmd') in ('moveTo', 'lineTo'):
                    pts = c.get('pts', [])
                    if i < cnt + len(pts):
                        return pts[i - cnt]
                    cnt += len(pts)
        return None

    def set_vertex(self, index: int, x: float, y: float):
        i = int(index)
        cnt = 0
        for p in self.paths:
            cmds = p.get('path_cmds') or []
            for c in cmds:
                if c.get('cmd') in ('moveTo', 'lineTo'):
                    pts = c.get('pts', [])
                    if i < cnt + len(pts):
                        pts[i - cnt] = (float(x), float(y))
                        return None
                    cnt += len(pts)
        raise IndexError('vertex index out of range')

    # Style setters: accept either an rgba tuple or single value(s)
    def _normalize_color(self, color: Any) -> Optional[Tuple[float, float, float, float]]:
        if color is None:
            return None
        if isinstance(color, tuple) or isinstance(color, list):
            vals = list(color)
            if len(vals) == 3:
                r, g, b = vals
                a = 1.0
            elif len(vals) >= 4:
                r, g, b, a = vals[0], vals[1], vals[2], vals[3]
            else:
                return None
            # convert 0-255 ints to 0-1 floats
            try:
                if any(v > 1 for v in (r, g, b)):
                    r = float(r) / 255.0
                    g = float(g) / 255.0
                    b = float(b) / 255.0
                return (float(r), float(g), float(b), float(a))
            except Exception:
                return None
        # accept strings by delegating to parser
        if isinstance(color, str):
            return _parse_color(color)
        # single numeric
        try:
            v = float(color)
            return (v, v, v, 1.0)
        except Exception:
            return None

    def set_fill(self, *args):
        c = args[0] if args else None
        rgba = self._normalize_color(c)
        # apply to top-level style or each path if present
        if not self.paths:
            self.paths.append({'path_cmds': None, 'style': {}})
        try:
            for p in self.paths:
                st = p.setdefault('style', {})
                st['fill_rgba'] = rgba
        except Exception:
            pass
        return None

    def set_stroke(self, *args):
        c = args[0] if args else None
        rgba = self._normalize_color(c)
        if not self.paths:
            self.paths.append({'path_cmds': None, 'style': {}})
        try:
            for p in self.paths:
                st = p.setdefault('style', {})
                st['stroke_rgba'] = rgba
        except Exception:
            pass
        return None

    # Transform helpers (record transforms but do not mutate geometry)
    def translate(self, tx: float, ty: float = 0.0):
        try:
            self._tx += float(tx)
            self._ty += float(ty)
        except Exception:
            pass
        return None

    def rotate_x(self, *args, **kwargs):
        return None

    def rotate_y(self, *args, **kwargs):
        return None

    def rotate_z(self, *args, **kwargs):
        return None

    def rotate(self, angle: float):
        try:
            self._rotation += float(angle)
        except Exception:
            pass
        return None

    def scale(self, sx: float, sy: Optional[float] = None):
        try:
            self._sx *= float(sx)
            if sy is None:
                self._sy *= float(sx)
            else:
                self._sy *= float(sy)
        except Exception:
            pass
        return None

    def reset_matrix(self):
        self._tx = 0.0
        self._ty = 0.0
        self._sx = 1.0
        self._sy = 1.0
        self._rotation = 0.0
        return None

    # Convenience: compute tight bounds across all skia_paths when caller
    # needs a numeric width/height but the SVG didn't include explicit
    # document dimensions.
    def compute_document_size(self) -> Tuple[float, float]:
        try:
            if self.width is not None and self.height is not None:
                return float(self.width), float(self.height)
        except Exception:
            pass
        # fallback: union bounds of constituent paths
        left = top = float('inf')
        right = bottom = float('-inf')
        any_pts = False
        for p in getattr(self, 'skia_paths', []) or []:
            try:
                b = p.computeTightBounds()
                left_bound = float(b.left())
                top_bound = float(b.top())
                right_bound = float(b.right())
                bottom_bound = float(b.bottom())
                left = min(left, left_bound)
                top = min(top, top_bound)
                right = max(right, right_bound)
                bottom = max(bottom, bottom_bound)
                any_pts = True
            except Exception:
                try:
                    br = p.getBounds()
                    left_bound = float(br.left())
                    top_bound = float(br.top())
                    right_bound = float(br.right())
                    bottom_bound = float(br.bottom())
                    left = min(left, left_bound)
                    top = min(top, top_bound)
                    right = max(right, right_bound)
                    bottom = max(bottom, bottom_bound)
                    any_pts = True
                except Exception:
                    continue
        if not any_pts:
            return 0.0, 0.0
        w = max(0.0, right - left)
        h = max(0.0, bottom - top)
        return w, h


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
    if s is None:
        return None
    s = s.strip()
    # hex
    m = re.match(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", s)
    if m:
        hexs = m.group(1)
        if len(hexs) == 3:
            r = float(int(hexs[0] * 2, 16))
            g = float(int(hexs[1] * 2, 16))
            b = float(int(hexs[2] * 2, 16))
        else:
            r = float(int(hexs[0:2], 16))
            g = float(int(hexs[2:4], 16))
            b = float(int(hexs[4:6], 16))
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
        "black": (0.0, 0.0, 0.0, 1.0),
        "white": (1.0, 1.0, 1.0, 1.0),
        "red": (1.0, 0.0, 0.0, 1.0),
        "green": (0.0, 1.0, 0.0, 1.0),
        "blue": (0.0, 0.0, 1.0, 1.0),
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
    if parse_path is None:
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
        # parse_path may be provided by the optional svg.path package
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
            k, val = part.split(":", 1)
            style[k.strip()] = val.strip()
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
    except Exception:
        # try decoding as text then parse
        try:
            root = ET.fromstring(text.decode("utf-8").lstrip())
        except Exception:
            raise

    shape = PCShape()

    # Try to populate document-level width/height from the SVG root. Prefer
    # the viewBox (which provides explicit document coordinates), falling
    # back to width/height attributes if present.
    try:
        vb_raw = root.get('viewBox') or root.get('viewbox') or ''
        vb = vb_raw.strip()
        if vb:
            parts = [p for p in re.split(r"[\s,]+", vb) if p]
            if len(parts) >= 4:
                try:
                    shape.width = float(parts[2])
                    shape.height = float(parts[3])
                except Exception:
                    pass
        else:
            w = root.get('width')
            h = root.get('height')
            if w is not None:
                try:
                    shape.width = _parse_number(w)
                except Exception:
                    shape.width = None
            if h is not None:
                try:
                    shape.height = _parse_number(h)
                except Exception:
                    shape.height = None
    except Exception:
        # best-effort: leave width/height as None if parsing fails
        pass

    # Build a simple id -> element map to resolve <use> and <defs> references
    id_map: Dict[str, ET.Element] = {}
    for el in root.iter():
        eid = el.get('id')
        if eid:
            id_map[eid] = el


    def recurse(node: ET.Element, inherited_matrix: Tuple[float, float, float, float, float, float], parent_shape: PCShape):
        # compute this node's transform
        t = node.get("transform")
        local = parse_matrix(t) if t else (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        total = _compose_matrix(inherited_matrix, local)

        tag = node.tag.split("}")[-1]
        style = _parse_style(node)

        path_obj = None
        try:
            if tag == "g":
                # group: recurse into children. For loader compatibility we
                # flatten group contents into the parent shape so callers
                # receive skia_paths at the top-level (many sketches expect
                # shapes to contain paths regardless of grouping). The
                # transform `total` is still propagated so child geometry is
                # transformed correctly.
                for ch in node:
                    recurse(ch, total, parent_shape)
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
                    recurse(ch, total, parent_shape)
                return
        except Exception:
            path_obj = None

        if path_obj is not None:
            _apply_matrix_to_path(path_obj, total)
            parent_shape.skia_paths.append(path_obj)
            parent_shape.paths.append({"style": style, "tag": tag})

        # handle <use> which references another element by id (href="#id")
        if tag == 'use':
            # SVG may use xlink:href or href (SVG2)
            href = node.get('{http://www.w3.org/1999/xlink}href') or node.get('href') or node.get('xlink:href')
            if href:
                ref = href.lstrip('#')
                ref_el = id_map.get(ref)
                if ref_el is not None:
                    # apply use-specific x/y as an extra translate
                    ux = _parse_number(node.get('x'), 0.0)
                    uy = _parse_number(node.get('y'), 0.0)
                    use_mat = _compose_matrix(total, (1.0, 0.0, 0.0, 1.0, ux, uy))
                    recurse(ref_el, use_mat, parent_shape)

        # recurse children for nested shapes (when not handled above)
        for ch in node:
            recurse(ch, total, parent_shape)

    recurse(root, (1.0, 0.0, 0.0, 1.0, 0.0, 0.0), shape)
    return shape


# compatibility alias expected by package exports
def load_shape(path: str) -> PCShape:
    """Compatibility wrapper used by package-level imports.

    Historically callers used `load_shape`; keep that alias to avoid
    import errors.
    """
    return load_svg(path)

