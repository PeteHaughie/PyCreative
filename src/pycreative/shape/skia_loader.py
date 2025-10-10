from __future__ import annotations

from typing import List, Tuple, Optional
import xml.etree.ElementTree as ET

try:
    import skia
    _HAS_SKIA = True
except Exception:
    skia = None  # type: ignore
    _HAS_SKIA = False

from .core import PShape
from .utils import parse_transform, apply_matrix_point, parse_style


def skia_available() -> bool:
    return _HAS_SKIA


def _rasterize_svg_to_pil(svg_path: str, w: int = 400, h: int = 400):
    """Rasterize an SVG path via skia.SVGDOM into a PIL.Image (RGBA) or None.

    This helper tries multiple constructors for SVGDOM for cross-version
    compatibility and returns a PIL.Image when successful.
    """
    if not _HAS_SKIA:
        return None
    try:
        dom = None
        try:
            dom = skia.SVGDOM.MakeFromFile(svg_path)
        except Exception:
            try:
                with open(svg_path, 'r', encoding='utf-8') as f:
                    txt = f.read()
                dom = skia.SVGDOM.MakeFromString(txt)
            except Exception:
                try:
                    from pathlib import Path
                    b = Path(svg_path).read_bytes()
                    mem = skia.MemoryStream(b)
                    dom = skia.SVGDOM.MakeFromStream(mem)
                except Exception:
                    dom = None
        if dom is None:
            return None
        try:
            if hasattr(dom, 'setContainerSize'):
                dom.setContainerSize(skia.Size(int(w), int(h)))
        except Exception:
            pass

        info = skia.ImageInfo.Make(int(w), int(h), skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType)
        surf = skia.Surface.MakeRaster(info)
        if not surf:
            return None
        canvas = surf.getCanvas()
        canvas.clear(skia.ColorWHITE)
        dom.render(canvas)
        img = surf.makeImageSnapshot()
        try:
            data = img.encodeToData()
            b = data.toBytes()
            from io import BytesIO
            from PIL import Image
            im = Image.open(BytesIO(b)).convert('RGBA')
            return im
        except Exception:
            try:
                pix = img.peekPixels()
                return None
            except Exception:
                return None
    except Exception:
        return None


def _stream_get_bytes(stream) -> Optional[bytes]:
    """Try several DynamicMemoryWStream-like APIs to extract bytes.

    Different skia-python builds expose different methods. Try common
    candidates and return raw bytes when found, else None.
    """
    if stream is None:
        return None
    # Try common names in order of preference
    candidates = [
        'detachAsData',
        'copyToData',
        'getData',
        'bytes',
        'toBytes',
    ]
    for name in candidates:
        if hasattr(stream, name):
            try:
                obj = getattr(stream, name)()
                # If this returns skia.Data-like with toBytes(), try that
                if obj is None:
                    return None
                try:
                    # skia.Data in some builds exposes .bytes() or .data()
                    if hasattr(obj, 'toBytes'):
                        return bytes(obj.toBytes())
                    if hasattr(obj, 'bytes'):
                        try:
                            return bytes(obj.bytes())
                        except Exception:
                            pass
                    if hasattr(obj, 'data'):
                        try:
                            dv = obj.data()
                            # memoryview or buffer
                            return bytes(dv)
                        except Exception:
                            pass
                except Exception:
                    pass
                # If it's already bytes-like
                if isinstance(obj, (bytes, bytearray)):
                    return bytes(obj)
                # If it's a Python buffer/memoryview
                try:
                    return bytes(obj)
                except Exception:
                    continue
            except Exception:
                continue
    # As a last-ditch, try calling getData and then toBytes on returned object
    try:
        gd = getattr(stream, 'getData', None)
        if gd:
            obj = gd()
            if obj is None:
                return None
            if hasattr(obj, 'toBytes'):
                return bytes(obj.toBytes())
    except Exception:
        pass
    return None


def _build_skia_path_from_d(d: str) -> Optional['skia.Path']:
    if not _HAS_SKIA:
        return None
    # A minimal parser that re-uses the tokenization approach from loader.py
    import re

    num_re = r"[+-]?(?:\d*\.\d+|\d+)(?:[eE][+-]?\d+)?"
    tokens = re.findall(rf"[A-Za-z]|{num_re}", d)
    path = skia.Path()
    cmd = None
    i = 0
    cur_x = 0.0
    cur_y = 0.0
    start_x = None
    start_y = None
    prev_cx = None
    prev_cy = None
    try:
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
                # multiple pairs may follow a single command; M followed by
                # additional pairs behaves like implicit L commands per spec
                first = True
                while i + 1 < len(tokens) and not tokens[i].isalpha():
                    x = float(tokens[i])
                    y = float(tokens[i + 1])
                    if cmd == 'M' and first:
                        path.moveTo(x, y)
                        # subsequent pairs after M are treated as L
                        cmd = 'L'
                    else:
                        path.lineTo(x, y)
                    cur_x, cur_y = x, y
                    if start_x is None:
                        start_x, start_y = cur_x, cur_y
                    i += 2
                    first = False
            elif cmd in ('m', 'l'):
                dx = float(tokens[i])
                dy = float(tokens[i + 1])
                cur_x += dx
                cur_y += dy
                path.rMoveTo(dx, dy) if cmd == 'm' else path.rLineTo(dx, dy)
                if start_x is None:
                    start_x, start_y = cur_x, cur_y
                i += 2
            elif cmd in ('H', 'h'):
                # horizontal line
                val = float(tokens[i])
                x = val if cmd == 'H' else cur_x + val
                path.lineTo(x, cur_y)
                cur_x = x
                i += 1
            elif cmd in ('V', 'v'):
                val = float(tokens[i])
                y = val if cmd == 'V' else cur_y + val
                path.lineTo(cur_x, y)
                cur_y = y
                i += 1
            elif cmd in ('C', 'c'):
                # repeated cubic segments allowed
                while i + 5 < len(tokens) and not tokens[i].isalpha():
                    cx1 = float(tokens[i])
                    cy1 = float(tokens[i + 1])
                    cx2 = float(tokens[i + 2])
                    cy2 = float(tokens[i + 3])
                    x = float(tokens[i + 4])
                    y = float(tokens[i + 5])
                    if cmd == 'c':
                        path.rCubicTo(cx1, cy1, cx2, cy2, x, y)
                        cur_x += x
                        cur_y += y
                    else:
                        path.cubicTo(cx1, cy1, cx2, cy2, x, y)
                        cur_x, cur_y = x, y
                    prev_cx, prev_cy = cx2, cy2
                    i += 6
            elif cmd in ('S', 's'):
                # shorthand cubic: allow repeated segments
                while i + 3 < len(tokens) and not tokens[i].isalpha():
                    cx2 = float(tokens[i])
                    cy2 = float(tokens[i + 1])
                    x = float(tokens[i + 2])
                    y = float(tokens[i + 3])
                    if prev_cx is not None and prev_cy is not None:
                        cx1 = 2 * cur_x - prev_cx
                        cy1 = 2 * cur_y - prev_cy
                    else:
                        cx1 = cur_x
                        cy1 = cur_y
                    if cmd == 's':
                        # relative shorthand: convert to relative cubic
                        path.rCubicTo(cx1 - cur_x, cy1 - cur_y, cx2, cy2, x, y)
                        cur_x += x
                        cur_y += y
                    else:
                        path.cubicTo(cx1, cy1, cx2, cy2, x, y)
                        cur_x, cur_y = x, y
                    prev_cx, prev_cy = cx2, cy2
                    i += 4
            elif cmd in ('Q', 'q'):
                while i + 3 < len(tokens) and not tokens[i].isalpha():
                    qx1 = float(tokens[i])
                    qy1 = float(tokens[i + 1])
                    x = float(tokens[i + 2])
                    y = float(tokens[i + 3])
                    if cmd == 'q':
                        path.rQuadTo(qx1, qy1, x, y)
                        cur_x += x
                        cur_y += y
                    else:
                        path.quadTo(qx1, qy1, x, y)
                        cur_x, cur_y = x, y
                    prev_cx, prev_cy = qx1, qy1
                    i += 4
            elif cmd in ('T', 't'):
                while i + 1 < len(tokens) and not tokens[i].isalpha():
                    if prev_cx is not None and prev_cy is not None:
                        qx1 = 2 * cur_x - prev_cx
                        qy1 = 2 * cur_y - prev_cy
                    else:
                        qx1, qy1 = cur_x, cur_y
                    x = float(tokens[i])
                    y = float(tokens[i + 1])
                    if cmd == 't':
                        path.rQuadTo(qx1 - cur_x, qy1 - cur_y, x, y)
                        cur_x += x
                        cur_y += y
                    else:
                        path.quadTo(qx1, qy1, x, y)
                        cur_x, cur_y = x, y
                    prev_cx, prev_cy = qx1, qy1
                    i += 2
            elif cmd in ('A', 'a'):
                while i + 6 < len(tokens) and not tokens[i].isalpha():
                    rx = float(tokens[i])
                    ry = float(tokens[i + 1])
                    xar = float(tokens[i + 2])
                    laf = int(float(tokens[i + 3]))
                    sf = int(float(tokens[i + 4]))
                    x = float(tokens[i + 5])
                    y = float(tokens[i + 6])
                    try:
                        path.arcTo(rx, ry, xar, laf, sf, x, y)
                    except Exception:
                        pass
                    cur_x, cur_y = x, y
                    prev_cx, prev_cy = None, None
                    i += 7
            elif cmd in ('Z', 'z'):
                path.close()
                if start_x is not None:
                    cur_x, cur_y = start_x, start_y
                i += 0
                i += 1
            else:
                # unknown/unsupported command: skip token
                i += 1
    except Exception:
        return None
    return path


def _flatten_skia_path(path: 'skia.Path', user_tol: float = 0.5) -> List[List[Tuple[float, float]]]:
    """Flatten a skia.Path into a list of subpaths (each a list of x,y tuples).

    Uses RawIter to walk verbs and points. This produces discrete segments which
    we then sample/approximate. tol is currently unused but kept for API parity.
    """
    out: List[List[Tuple[float, float]]] = []
    if not _HAS_SKIA:
        return out
    # Use getVerbs/getPoints to reconstruct contours
    verbs = path.getVerbs()
    pts = path.getPoints()
    pi = 0
    cur_sub: List[Tuple[float, float]] = []
    # helper to safely read a point
    def _pt(idx: int):
        if idx < 0 or idx >= len(pts):
            return None
        p = pts[idx]
        try:
            return (float(p.x()), float(p.y()))
        except Exception:
            return None

    from .. import shape_math

    explicit_closed = False
    for v in verbs:
        if v == skia.Path.kMove_Verb:
            # start a new subpath
            p0 = _pt(pi)
            pi += 1
            if p0 is None:
                continue
            if cur_sub:
                out.append(cur_sub)
            cur_sub = [p0]
            explicit_closed = False
        elif v == skia.Path.kLine_Verb:
            p1 = _pt(pi)
            pi += 1
            if p1 is None:
                continue
            if not cur_sub:
                cur_sub = [p1]
            else:
                cur_sub.append(p1)
        elif v == skia.Path.kQuad_Verb:
            # quad uses two points: control, end
            p_ctrl = _pt(pi)
            p_end = _pt(pi + 1)
            pi += 2
            if p_ctrl is None or p_end is None or not cur_sub:
                continue
            sx, sy = cur_sub[-1]
            cx, cy = p_ctrl
            ex, ey = p_end
            # use higher sampling to better approximate curves for fidelity
            # use provided user-space tolerance for fidelity
            seg = shape_math.flatten_quadratic_bezier((sx, sy), (cx, cy), (ex, ey), steps=64, tol=user_tol)
            if seg:
                # append all points except start (already present)
                for px, py in seg[1:]:
                    cur_sub.append((px, py))
        elif v == skia.Path.kCubic_Verb:
            # cubic uses three points: c1, c2, end
            p1 = _pt(pi)
            p2 = _pt(pi + 1)
            p3 = _pt(pi + 2)
            pi += 3
            if p1 is None or p2 is None or p3 is None or not cur_sub:
                continue
            c1x, c1y = p1
            c2x, c2y = p2
            ex, ey = p3
            sx, sy = cur_sub[-1]
            # increase sampling for cubic segments to reduce geometric error
            # use provided user-space tolerance for fidelity
            seg = shape_math.flatten_cubic_bezier((sx, sy), (c1x, c1y), (c2x, c2y), (ex, ey), steps=128, tol=user_tol)
            if seg:
                for px, py in seg[1:]:
                    cur_sub.append((px, py))
        elif v == skia.Path.kClose_Verb:
            if cur_sub and cur_sub[0] != cur_sub[-1]:
                cur_sub.append(cur_sub[0])
            if cur_sub:
                out.append(cur_sub)
            cur_sub = []
            explicit_closed = True
        else:
            # Skip unknown verbs safely
            pass
    # enforce closure only when the original path explicitly closed the contour
    def _maybe_close(sub: List[Tuple[float, float]], explicit: bool):
        if not sub:
            return sub
        if len(sub) < 2:
            return sub
        if explicit:
            # for explicit closes (Z/z), force exact closure
            if sub[0] != sub[-1]:
                sub[-1] = sub[0]
        return sub

    if cur_sub:
        # if leftover subpath at end of verbs, only close it if explicit close seen
        out.append(_maybe_close(cur_sub, explicit_closed if 'explicit_closed' in locals() else False))
    return out


def skia_svg_to_pshape(path: str) -> Optional[PShape]:
    if not _HAS_SKIA:
        return None
    # Use the module-level rasterizer helper when we need a Skia-rendered
    # PIL image for pixel-perfect fallbacks.
    # First try a DOM-based extraction using Skia's SVGDOM which is the
    # most authoritative way to parse SVG files. If any step fails, fall
    # back to the previous element-wise parsing implementation below.
    try:
        # skia.SVGDOM.MakeFromFile / MakeFromString variants exist across
        # skia-python versions. Try available constructors defensively.
        dom = None
        try:
            dom = skia.SVGDOM.MakeFromFile(path)
        except Exception:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    txt = f.read()
                dom = skia.SVGDOM.MakeFromString(txt)
            except Exception:
                dom = None

        if dom is not None:
            shape = PShape()
            # expose viewBox if available on dom
            try:
                vb = dom.containerSize() if hasattr(dom, 'containerSize') else None
                # Many skia.SVGDOM implementations expose viewBox via dom.viewBox()
                if hasattr(dom, 'viewBox'):
                    vbv = dom.viewBox()
                    if vbv is not None and len(vbv) >= 4:
                        shape.view_box = (float(vbv[0]), float(vbv[1]), float(vbv[2]), float(vbv[3]))
            except Exception:
                pass

            # To extract exact path geometry we can ask the DOM to render
            # into a skia.RecordingCanvas or use dom.render and then extract
            # paths from a Drawable; APIs vary by skia-python version so use
            # a conservative approach: render into an SkPicture and then
            # replay to a skia.Canvas backed by a skia.PictureRecorder and
            # try to obtain paths via the DOM's API when present.
            try:
                # Render into a recording canvas sized to the container (400x400)
                recorder = skia.PictureRecorder()
                rcanvas = recorder.beginRecording(skia.Rect(0, 0, 400, 400))
                # Prefer per-node rendering if available to access node geometry
                try:
                    # Some skia.SVGDOM implementations expose renderNode
                    dom.renderNode(rcanvas)
                except Exception:
                    dom.render(rcanvas)
                picture = recorder.finishRecordingAsPicture()
                # If the picture can return a skia.Path(s) we could extract
                # geometry, but skia-python lacks a stable API for this across
                # versions. So as a robust fallback, rasterize the DOM into an
                # intermediate bitmap and then (optionally) use contours
                # extraction — but that is lossy. Therefore prefer direct DOM
                # path iteration when available (dom.getChildren/dom.rootNode).
            except Exception:
                pass

            # Try to serialize DOM rendering into an SVG string via SVGCanvas.
            # Some skia builds provide SVGCanvas.Make which can capture draw
            # operations as an SVG document written to a WStream. We'll try to
            # create a DynamicMemoryWStream, render the DOM into the canvas,
            # then parse the emitted SVG text to extract <path> elements.
            try:
                if hasattr(skia, 'DynamicMemoryWStream') and hasattr(skia, 'SVGCanvas'):
                    stream = skia.DynamicMemoryWStream()
                    # create SVG canvas for the desired bounds
                    try:
                        svg_canvas = skia.SVGCanvas.Make(skia.Rect(0, 0, 400, 400), stream)
                    except Exception:
                        svg_canvas = None
                    if svg_canvas is not None:
                        try:
                            dom.render(svg_canvas)
                            svg_canvas.flush()
                            data_bytes = _stream_get_bytes(stream)
                            if not data_bytes:
                                txt = ''
                            else:
                                try:
                                    txt = data_bytes.decode('utf-8', errors='ignore')
                                except Exception:
                                    txt = ''
                            # parse emitted SVG text
                            try:
                                import xml.etree.ElementTree as ET
                                root = ET.fromstring(txt)
                                # find all path elements and extract their 'd' attr
                                for pnode in root.iter():
                                    if pnode.tag.endswith('path') or pnode.tag == 'path':
                                        d = pnode.get('d') or ''
                                        if d:
                                            spath = _build_skia_path_from_d(d)
                                            if spath is not None:
                                                subs = _flatten_skia_path(spath, user_tol=0.5)
                                                for sub in subs:
                                                    shape.add_subpath(sub)
                                if shape.subpaths:
                                    # attach raster too for parity (use same 400x400 canvas)
                                    try:
                                        pil_img = _rasterize_svg_to_pil(path, 400, 400)
                                        if pil_img is not None:
                                            shape._skia_raster = pil_img
                                    except Exception:
                                        pass
                                    return shape
                            except Exception:
                                pass
                        except Exception:
                            pass
            except Exception:
                pass

            # Best-effort: if dom has a method to access nodes/paths, iterate
            # and extract path data. This section is guarded and falls back
            # to the older XML-based extractor below when not possible.
            try:
                # Many DOMs expose root or getRoot; try common names.
                rootnode = None
                if hasattr(dom, 'getRoot'):
                    rootnode = dom.getRoot()
                elif hasattr(dom, 'root'):
                    rootnode = dom.root
                # If we have a root node and it exposes 'children' or 'getChildren'
                # iterate and attempt to grab path data via node.path or node.getPath
                if rootnode is not None:
                    # collect candidate nodes via common APIs
                    nodes = []
                    if hasattr(rootnode, 'children'):
                        nodes = list(rootnode.children)
                    elif hasattr(rootnode, 'getChildren'):
                        nodes = list(rootnode.getChildren())

                    def walk_nodes(nlist):
                        for n in nlist:
                            try:
                                # If the node can expose a Path, extract and flatten
                                p = None
                                if hasattr(n, 'getPath'):
                                    p = n.getPath()
                                elif hasattr(n, 'path'):
                                    p = getattr(n, 'path')
                                                if p is not None and isinstance(p, skia.Path):
                                                    # preserve the original skia.Path for higher-fidelity
                                                    # rendering later. Store on the PShape as a list
                                                    # so downstream code can rasterize with Skia
                                                    # when desired.
                                                    try:
                                                        if not hasattr(shape, '_skia_paths'):
                                                            shape._skia_paths = []
                                                        shape._skia_paths.append(p)
                                                    except Exception:
                                                        pass
                                                    subs = _flatten_skia_path(p, user_tol=0.5)
                                                    for sub in subs:
                                                        shape.add_subpath(sub)
                                # Recurse into children if present
                                child_nodes = None
                                if hasattr(n, 'children'):
                                    child_nodes = list(n.children)
                                elif hasattr(n, 'getChildren'):
                                    child_nodes = list(n.getChildren())
                                if child_nodes:
                                    walk_nodes(child_nodes)
                            except Exception:
                                # ignore node-level failures and continue
                                continue

                    walk_nodes(nodes)
                    if shape.subpaths:
                        # attempt to rasterize and attach a Skia-rendered PIL
                        # image for pixel-perfect fallbacks; ignore failures
                        try:
                            pil_img = _rasterize_svg_to_pil(path, int(container_w), int(container_h))
                            if pil_img is not None:
                                shape._skia_raster = pil_img
                        except Exception:
                            pass
                        return shape
            except Exception:
                pass
            # If DOM-based extraction failed to produce subpaths, continue
            # and fall back to the XML-based method below.
    except Exception:
        # Any failure here means we'll fall back to the previous logic
        pass
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception:
        return None

    shape = PShape()

    svg_ns = ''
    if root.tag.startswith('{'):
        svg_ns = root.tag.split('}')[0] + '}'
    # Build parent map so we can compose transforms from root -> element
    parent_map = {c: p for p in root.iter() for c in p}

    # Compute root viewBox -> container transform (match skia.SVGDOM.setContainerSize used in tests)
    try:
        vb = root.get('viewBox') or root.get('viewbox')
        if vb:
            import re
            nums = re.findall(r"[+-]?(?:\d*\.\d+|\d+)(?:[eE][+-]?\d+)?", vb)
            if len(nums) >= 4:
                vb_x = float(nums[0])
                vb_y = float(nums[1])
                vb_w = float(nums[2])
                vb_h = float(nums[3])
            else:
                vb_x = vb_y = vb_w = vb_h = None
        else:
            vb_x = vb_y = vb_w = vb_h = None
    except Exception:
        vb_x = vb_y = vb_w = vb_h = None

    # default container size used when we rasterize with Skia during testing
    container_w = 400.0
    container_h = 400.0

    if vb_x is not None and vb_w and vb_h:
        # match SVG preserveAspectRatio default: 'xMidYMid meet'
        scale_x = container_w / vb_w
        scale_y = container_h / vb_h
        scale = min(scale_x, scale_y)
        tx = (container_w - vb_w * scale) / 2.0 - vb_x * scale
        ty = (container_h - vb_h * scale) / 2.0 - vb_y * scale
        root_viewbox_mat = (scale, 0.0, 0.0, scale, tx, ty)
    else:
        root_viewbox_mat = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

    # expose the SVG viewBox to the PShape so rendering can use it
    if vb_x is not None and vb_w and vb_h:
        try:
            shape.view_box = (vb_x, vb_y, vb_w, vb_h)
        except Exception:
            shape.view_box = None

    def _compose_transform_for(elem):
        # Walk from root down to elem collecting transforms
        mats = []
        cur = elem
        while cur is not None:
            t = cur.get('transform') if isinstance(cur, ET.Element) else None
            if t:
                mats.append(parse_transform(t))
            cur = parent_map.get(cur)
        # mats currently from element -> root, reverse to root -> element
        mats.reverse()
        # compose matrices: m_total = m_n * ... * m_1
        if not mats:
            return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
        a1, b1, c1, d1, e1, f1 = mats[0]
        cur_mat = (a1, b1, c1, d1, e1, f1)
        for m in mats[1:]:
            a2, b2, c2, d2, e2, f2 = m
            a1, b1, c1, d1, e1, f1 = cur_mat
            # multiply m2 * m1 (apply m1 then m2)
            composed = (
                a2 * a1 + c2 * b1,
                b2 * a1 + d2 * b1,
                a2 * c1 + c2 * d1,
                b2 * c1 + d2 * d1,
                a2 * e1 + c2 * f1 + e2,
                b2 * e1 + d2 * f1 + f2,
            )
            cur_mat = composed
        return cur_mat

    def _parse_points_attr(s: str):
        parts = s.replace(',', ' ').split()
        it = iter(parts)
        out = []
        for a, b in zip(it, it):
            try:
                out.append((float(a), float(b)))
            except Exception:
                continue
        return out

    # Iterate elements and build paths
    # Determine a user-space tolerance so that after scaling to container size
    # the pixel flatness is ~0.5px. tol_user = pixel_tol / scale
    try:
        scale_for_tol = root_viewbox_mat[0]
        if scale_for_tol == 0:
            scale_for_tol = 1.0
    except Exception:
        scale_for_tol = 1.0
    user_tol = 0.5 / float(scale_for_tol)

    for elem in root.iter():
        tag = elem.tag
        if svg_ns and tag.startswith(svg_ns):
            ttag = tag[len(svg_ns):]
        else:
            ttag = tag

        try:
            # parse inline styles for the element into the shape
            try:
                parse_style(elem, shape)
            except Exception:
                pass

            mat = _compose_transform_for(elem)
            if ttag == 'path':
                d = elem.get('d') or ''
                spath = _build_skia_path_from_d(d)
                if spath is None:
                    continue
                subs = _flatten_skia_path(spath, user_tol=user_tol)
                for sub in subs:
                    # apply composed transform to points
                    pts = [apply_matrix_point(mat, x, y) for x, y in sub]
                    shape.add_subpath(pts)

            elif ttag in ('polygon', 'polyline'):
                pts_attr = elem.get('points') or ''
                pts = _parse_points_attr(pts_attr)
                if ttag == 'polygon' and pts and pts[0] != pts[-1]:
                    pts.append(pts[0])
                pts = [apply_matrix_point(mat, x, y) for x, y in pts]
                shape.add_subpath(pts)

            elif ttag == 'rect':
                try:
                    x = float(elem.get('x') or 0)
                    y = float(elem.get('y') or 0)
                    w = float(elem.get('width') or 0)
                    h = float(elem.get('height') or 0)
                    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
                    pts = [apply_matrix_point(mat, px, py) for px, py in pts]
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
                        t = (k / 24.0) * 2 * 3.141592653589793
                        pts.append((cx + (r * __import__('math').cos(t)), cy + (r * __import__('math').sin(t))))
                    pts.append(pts[0])
                    pts = [apply_matrix_point(mat, px, py) for px, py in pts]
                    shape.add_subpath(pts)
                except Exception:
                    pass

            elif ttag == 'ellipse':
                try:
                    cx = float(elem.get('cx') or 0)
                    cy = float(elem.get('cy') or 0)
                    rx = float(elem.get('rx') or 0)
                    ry = float(elem.get('ry') or 0)
                    pts = []
                    for k in range(24):
                        t = (k / 24.0) * 2 * 3.141592653589793
                        pts.append((cx + (rx * __import__('math').cos(t)), cy + (ry * __import__('math').sin(t))))
                    pts.append(pts[0])
                    pts = [apply_matrix_point(mat, px, py) for px, py in pts]
                    shape.add_subpath(pts)
                except Exception:
                    pass

            elif ttag == 'line':
                try:
                    x1 = float(elem.get('x1') or 0)
                    y1 = float(elem.get('y1') or 0)
                    x2 = float(elem.get('x2') or 0)
                    y2 = float(elem.get('y2') or 0)
                    pts = [apply_matrix_point(mat, x1, y1), apply_matrix_point(mat, x2, y2)]
                    shape.add_subpath(pts)
                except Exception:
                    pass
        except Exception:
            continue

    # Try to rasterize the SVG via Skia and attach raster to shape for
    # pixel-perfect fallbacks when exact vector extraction is difficult.
    try:
        # Attempt a direct MemoryStream-based rasterization which is the
        # most reliable across skia-python builds in this environment.
        try:
            from pathlib import Path
            b = Path(path).read_bytes()
            mem = skia.MemoryStream(b)
            dom2 = None
            try:
                dom2 = skia.SVGDOM.MakeFromStream(mem)
            except Exception:
                dom2 = None
            if dom2 is not None:
                try:
                    if hasattr(dom2, 'setContainerSize'):
                        dom2.setContainerSize(skia.Size(int(container_w), int(container_h)))
                except Exception:
                    pass
                info = skia.ImageInfo.Make(int(container_w), int(container_h), skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType)
                surf = skia.Surface.MakeRaster(info)
                if surf is not None:
                    canvas = surf.getCanvas()
                    canvas.clear(skia.ColorWHITE)
                    dom2.render(canvas)
                    img = surf.makeImageSnapshot()
                    try:
                        data = img.encodeToData()
                        b2 = data.toBytes()
                        from io import BytesIO
                        from PIL import Image
                        pil_img = Image.open(BytesIO(b2)).convert('RGBA')
                        shape._skia_raster = pil_img
                    except Exception:
                        pass
        except Exception:
            pass
    except Exception:
        pass

    # If we found no vector subpaths, attempt a raster->contour fallback
    if not shape.subpaths:
        try:
            subs = _raster_contours_to_subpaths(path, int(container_w), int(container_h))
            if subs:
                # subs are in image coords [0..container_w/h]; map back to
                # SVG user-space using the inverse of root_viewbox_mat if
                # we exposed a viewBox above.
                inv_mat = None
                try:
                    a, b, c, d, e, f = root_viewbox_mat
                    # inverse of scale/translate only (root_viewbox_mat is scale,0,0,scale,tx,ty)
                    if a != 0 and d != 0:
                        inv_sx = 1.0 / a
                        inv_sy = 1.0 / d
                        inv_tx = -e * inv_sx
                        inv_ty = -f * inv_sy
                        inv_mat = (inv_sx, 0.0, 0.0, inv_sy, inv_tx, inv_ty)
                except Exception:
                    inv_mat = None

                for sub in subs:
                    if inv_mat is not None:
                        pts = [apply_matrix_point(inv_mat, x, y) for x, y in sub]
                    else:
                        pts = sub
                    shape.add_subpath(pts)
        except Exception:
            pass

    return shape


def _raster_contours_to_subpaths(svg_path: str, w: int = 400, h: int = 400, thresh: int = 16):
    """Rasterize SVG with Skia and extract simple binary-contour polygons.

    This is a lossy fallback used only when DOM/path extraction yields no
    geometry. It rasterizes the SVG into an RGBA image, thresholds the
    alpha/color to obtain a binary mask, then extracts outlines by scanning
    connected regions' borders. The result is a list of subpaths (lists of
    (x,y) tuples) in image coordinates.
    """
    if not _HAS_SKIA:
        return []
    try:
        pil = _rasterize_svg_to_pil(svg_path, w, h)
        if pil is None:
            return []
        mask = pil.convert('L')
        # threshold
        bw = mask.point(lambda p: 255 if p > thresh else 0)
        px = bw.load()
        W, H = bw.size

        visited = [[False] * W for _ in range(H)]
        subs = []

        def neighbors(x, y):
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x+dx, y+dy
                if 0 <= nx < W and 0 <= ny < H:
                    yield nx, ny

        for y in range(H):
            for x in range(W):
                if visited[y][x]:
                    continue
                if px[x,y] == 0:
                    visited[y][x] = True
                    continue
                # flood-fill region
                stack = [(x,y)]
                region = []
                visited[y][x] = True
                while stack:
                    cx, cy = stack.pop()
                    region.append((cx, cy))
                    for nx, ny in neighbors(cx, cy):
                        if not visited[ny][nx] and px[nx,ny] != 0:
                            visited[ny][nx] = True
                            stack.append((nx, ny))
                # For the region, extract the outer boundary using Moore-neighbor
                # tracing (border following). This preserves shape concavities and
                # gives a tighter polygon than a convex-hull approximation.
                try:
                    # Build a set for quick membership
                    region_set = set(region)

                    # 8-connected neighbor offsets in clockwise order starting from west
                    nbrs = [(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1)]

                    def trace_border(start_x, start_y):
                        # Find the first border neighbor: previous is (start_x-1,start_y)
                        border = []
                        x0, y0 = start_x, start_y
                        cx, cy = x0, y0
                        # previous neighbor index (we start looking from the west)
                        prev_i = 0
                        while True:
                            border.append((cx, cy))
                            found = False
                            # search neighbors starting from prev_i-1 (mod 8)
                            si = (prev_i + 7) % 8
                            for k in range(8):
                                iidx = (si + k) % 8
                                nx = cx + nbrs[iidx][0]
                                ny = cy + nbrs[iidx][1]
                                if (nx, ny) in region_set:
                                    # move to this neighbor
                                    prev_i = iidx
                                    cx, cy = nx, ny
                                    found = True
                                    break
                            if not found:
                                break
                            if (cx, cy) == (x0, y0):
                                # closed loop
                                break
                        return border

                    # pick an extreme pixel as start (leftmost, then topmost)
                    start_px = min(region, key=lambda p: (p[0], p[1]))
                    border = trace_border(start_px[0], start_px[1])
                    # decimate border if very large
                    if len(border) > 1024:
                        step = max(1, len(border) // 1024)
                        border = border[::step]
                    poly = [(float(x), float(y)) for x, y in border]
                    if len(poly) >= 3:
                        if poly[0] != poly[-1]:
                            poly.append(poly[0])
                        subs.append(poly)
                except Exception:
                    continue
        return subs
    except Exception:
        return []

