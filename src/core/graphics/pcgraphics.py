"""PCGraphics: offscreen drawing surface (headless-friendly).

This is a minimal, well-documented implementation intended to provide
the offscreen API used by examples and docs. It records drawing commands
to an engine `graphics` buffer when used in headless mode and provides
the common methods sketches expect: `begin_draw` / `end_draw`, simple
shape helpers, `save`, and basic properties.
"""
from __future__ import annotations

from typing import Any, List, Optional


class PCGraphics:
    """A lightweight PCGraphics surface used by examples and tests.

    In headless mode this surface records draw operations to the engine's
    `graphics` recorder when `end_draw()` is called. Presenters and real
    GPU backends can provide richer implementations that match this API.
    """

    def __init__(self, width: int, height: int, engine: Optional[Any] = None):
        self.width = int(width)
        self.height = int(height)
        self._engine = engine
        # If engine was not provided, try to resolve the current engine via
        # the public pycreative shim so create_graphics() doesn't need to
        # accept an engine parameter.
        if self._engine is None:
            try:
                import pycreative as _pc

                try:
                    self._engine = _pc._get_engine()
                except Exception:
                    self._engine = None
            except Exception:
                self._engine = None
        self._recording: List[dict] = []
        self._in_draw = False
        # Per-surface default state
        self._fill: tuple[int, int, int] = (255, 255, 255)
        self._stroke: tuple[int, int, int] = (0, 0, 0)
        self._stroke_weight: float = 1.0
        # drawing modes
        self._rect_mode = 'CORNER'
        self._ellipse_mode = 'CENTER'

    def begin_draw(self):
        self._in_draw = True
        # start a fresh command list for this frame
        self._recording.clear()

    def end_draw(self):
        """End drawing and record the collected ops to the engine recorder
        when available.
        """
        self._in_draw = False
        if self._engine is not None:
            try:
                g = getattr(self._engine, 'graphics', None)
                if g is not None:
                    # Normalize the PCGraphics recording format into the
                    # engine's expected {'op': name, 'args': {...}} shape.
                    cmds = []
                    seq = 0
                    for c in list(self._recording):
                        seq += 1
                        op = c.get('op')
                        args: dict[str, Any] = {}

                        # Background color -> r/g/b/(a)
                        if op == 'background' and 'color' in c:
                            col = c.get('color')
                            try:
                                if isinstance(col, (list, tuple)):
                                    if len(col) >= 3:
                                        args['r'] = int(col[0])
                                        args['g'] = int(col[1])
                                        args['b'] = int(col[2])
                                    if len(col) >= 4:
                                        args['a'] = int(col[3])
                            except Exception:
                                pass

                        for k, v in c.items():
                            if k == 'op':
                                continue
                            if op == 'background' and k == 'color':
                                continue
                            if op == 'stroke_weight' and k == 'w':
                                try:
                                    args['weight'] = float(v)
                                except Exception:
                                    args['weight'] = v
                                continue
                            # common passthrough keys
                            if k in ('x', 'y', 'w', 'h', 'r', 'fill', 'stroke', 'stroke_weight', 'mode', 'image', 'vertices', 'text_size', 'size'):
                                args[k] = v
                                continue
                            args[k] = v

                        cmds.append({'op': op, 'args': args, 'meta': {'seq': seq}})

                    try:
                        g.record('offscreen', width=self.width, height=self.height, ops=cmds)
                    except Exception:
                        pass
            except Exception:
                pass

    def rect_mode(self, mode: str):
        try:
            self._rect_mode = str(mode)
        except Exception:
            pass

    def ellipse_mode(self, mode: str):
        try:
            self._ellipse_mode = str(mode)
        except Exception:
            pass

    def pixels(self):
        """Return a context manager that yields a Pillow Image representing
        the current surface contents. Use as `with pg.pixels() as img:`.
        """
        class _CM:
            def __init__(self, parent):
                self._parent = parent

            def __enter__(self):
                return self._parent.to_pillow()

            def __exit__(self, exc_type, exc, tb):
                return False

        return _CM(self)

    def image(self, img, x, y, w=None, h=None):
        self._recording.append({'op': 'image', 'image': img, 'x': float(x), 'y': float(y), 'w': (float(w) if w is not None else None), 'h': (float(h) if h is not None else None)})

    # Convenience drawing helpers that mirror the sketch API but record
    # simple ops into the PCGraphics recording so tests and examples can
    # use the surface directly.
    def background(self, *args):
        # Accept grayscale or RGB
        if len(args) == 0:
            col = (0, 0, 0)
        elif len(args) == 1:
            v = args[0]
            try:
                iv = int(v)
                col = (iv, iv, iv)
            except Exception:
                col = v
        else:
            col = tuple(int(a) for a in args[:4])
        self._recording.append({'op': 'background', 'color': col})

    def fill(self, *args):
        if len(args) == 0:
            self._recording.append({'op': 'fill', 'fill': None})
            return
        if len(args) == 1:
            v = args[0]
            try:
                iv = int(v)
                col = (iv, iv, iv)
            except Exception:
                col = v
        else:
            col = tuple(int(a) for a in args[:4])
        self._recording.append({'op': 'fill', 'fill': col})

    def no_fill(self):
        self._recording.append({'op': 'fill', 'fill': None})

    def stroke(self, *args):
        if len(args) == 0:
            self._recording.append({'op': 'stroke', 'stroke': None})
            return
        if len(args) == 1:
            v = args[0]
            try:
                iv = int(v)
                col = (iv, iv, iv)
            except Exception:
                col = v
        else:
            col = tuple(int(a) for a in args[:4])
        self._recording.append({'op': 'stroke', 'stroke': col})

    def no_stroke(self):
        self._recording.append({'op': 'stroke', 'stroke': None})

    def stroke_weight(self, w):
        try:
            fw = float(w)
        except Exception:
            fw = w
        self._recording.append({'op': 'stroke_weight', 'w': fw})

    def rect(self, x, y, w, h, mode: Optional[str] = None):
        entry = {'op': 'rect', 'x': float(x), 'y': float(y), 'w': float(w), 'h': float(h)}
        if mode is not None:
            entry['mode'] = str(mode)
        # copy current fill/stroke/weight hints
        self._recording.append(entry)

    def square(self, x, y, size, mode: Optional[str] = None):
        self.rect(x, y, size, size, mode=mode)

    def ellipse(self, x, y, w, h, mode: Optional[str] = None):
        entry = {'op': 'ellipse', 'x': float(x), 'y': float(y), 'w': float(w), 'h': float(h)}
        if mode is not None:
            entry['mode'] = str(mode)
        self._recording.append(entry)

    def circle(self, x, y, r):
        self._recording.append({'op': 'circle', 'x': float(x), 'y': float(y), 'r': float(r)})

    def line(self, x1, y1, x2, y2):
        self._recording.append({'op': 'line', 'x1': float(x1), 'y1': float(y1), 'x2': float(x2), 'y2': float(y2)})

    def save(self, path: str):
        # Follow the same filename/template and path resolution conventions
        # as Engine.save_frame(): support '#' sequences in basenames and
        # resolve relative paths against the sketch folder when possible.
        import os

        try:
            try:
                frame_val = int(getattr(self._engine, 'frame_count', 0))
            except Exception:
                frame_val = 0

            if not path:
                path = f"offscreen-{frame_val:04d}.png"
            else:
                import re

                try:
                    dirpart = os.path.dirname(path)
                    base = os.path.basename(path)
                    if base and ('#' in base):
                        def _rep(m):
                            w = len(m.group(0))
                            return f"{frame_val:0{w}d}"

                        new_base = re.sub(r"#+", _rep, base)
                        path = os.path.join(dirpart, new_base) if dirpart else new_base
                except Exception:
                    pass
        except Exception:
            pass

        # Normalize relative paths against the sketch directory when possible
        try:
            if not os.path.isabs(path):
                sketch_dir = None
                try:
                    smod = getattr(self._engine, '_sketch_module', None)
                    if smod is not None:
                        sf = getattr(smod, '__file__', None)
                        if sf:
                            sketch_dir = os.path.dirname(os.path.abspath(sf))
                except Exception:
                    sketch_dir = None

                if sketch_dir is None:
                    try:
                        s = getattr(self._engine, 'sketch', None)
                        if s is not None:
                            sf = getattr(s, '__file__', None)
                            if sf:
                                sketch_dir = os.path.dirname(os.path.abspath(sf))
                    except Exception:
                        sketch_dir = None

                if sketch_dir is None:
                    sketch_dir = os.getcwd()

                try:
                    path = os.path.abspath(os.path.join(sketch_dir, path))
                except Exception:
                    path = os.path.abspath(path)
        except Exception:
            try:
                path = os.path.abspath(path)
            except Exception:
                pass

        # Prefer using the centralized Skia replayer when available so
        # offscreen saves match the engine/save_frame output. This will
        # produce identical snapshots when Skia is present.
        try:
            from core.io.skia_replayer import replay_to_image_skia
            import types

            try:
                temp_engine = types.SimpleNamespace()
                # Determine HiDPI scale if an engine/presenter is available
                sx = sy = 1.0
                try:
                    if self._engine is not None:
                        pres = getattr(self._engine, '_presenter', None)
                        if pres is not None:
                            # prefer explicit surface/backing sizes recorded on presenter
                            try:
                                bw_bh = getattr(pres, '_surface_size', None) or getattr(pres, '_backing_size', (None, None))
                                if isinstance(bw_bh, (list, tuple)) and len(bw_bh) >= 2:
                                    bw = bw_bh[0]
                                    bh = bw_bh[1]
                                else:
                                    bw = bh = None
                                lw_lh = getattr(pres, '_logical_size', (None, None))
                                try:
                                    lw, lh = lw_lh
                                except Exception:
                                    lw = lh = None
                                if bw and bh and lw and lh:
                                    sx = float(bw) / float(lw)
                                    sy = float(bh) / float(lh)
                            except Exception:
                                pass
                except Exception:
                    pass

                # Build commands in engine-expected shape and apply scaling
                cmds = []
                seq = 0
                for c in list(self._recording):
                    seq += 1
                    op = c.get('op')
                    args: dict[str, Any] = {}
                    # Helper to map color tuples into r/g/b/a keys for background
                    if op == 'background' and 'color' in c:
                        col = c.get('color')
                        try:
                            if isinstance(col, (list, tuple)):
                                if len(col) >= 3:
                                    args['r'] = int(col[0])
                                    args['g'] = int(col[1])
                                    args['b'] = int(col[2])
                                if len(col) >= 4:
                                    args['a'] = int(col[3])
                        except Exception:
                            pass
                    # Map and scale coordinates/dimensions carefully
                    # First, extract raw values for possible center->corner conversion
                    raw_x = c.get('x')
                    raw_y = c.get('y')
                    raw_w = c.get('w')
                    raw_h = c.get('h')
                    mode_val = (c.get('mode') or '').upper()

                    # If modes indicate CENTER semantics, convert to CORNER (top-left)
                    if mode_val == 'CENTER' and raw_x is not None and raw_y is not None and raw_w is not None and raw_h is not None:
                        try:
                            # compute logical top-left
                            raw_x = float(raw_x) - float(raw_w) / 2.0
                            raw_y = float(raw_y) - float(raw_h) / 2.0
                        except Exception:
                            pass

                    for k, v in c.items():
                        if k == 'op':
                            continue
                        # background handled above
                        if op == 'background' and k == 'color':
                            continue
                        # stroke_weight: map 'w' to 'weight' and do NOT scale
                        if op == 'stroke_weight' and k == 'w':
                            try:
                                args['weight'] = float(v)
                            except Exception:
                                args['weight'] = v
                            continue
                        # scale x,y
                        if k == 'x':
                            # prefer converted raw_x when present
                            try:
                                vx = float(raw_x) if raw_x is not None else float(v)
                                args['x'] = float(vx) * sx
                                continue
                            except Exception:
                                pass
                            if isinstance(v, (int, float)):
                                args['x'] = float(v) * sx
                                continue
                            continue
                        if k == 'y':
                            try:
                                vy = float(raw_y) if raw_y is not None else float(v)
                                args['y'] = float(vy) * sy
                                continue
                            except Exception:
                                pass
                            if isinstance(v, (int, float)):
                                args['y'] = float(v) * sy
                                continue
                            continue
                        # scale width/height for drawing ops; width -> sx, height -> sy
                        if k == 'w':
                            try:
                                vw = float(raw_w) if raw_w is not None else float(v)
                                args['w'] = float(vw) * sx
                            except Exception:
                                args['w'] = v
                            continue
                        if k == 'r':
                            # circle radius: scale by device pixel ratio
                            try:
                                vr = float(v)
                                args['r'] = float(vr) * sx
                            except Exception:
                                args['r'] = v
                            continue
                        # stroke weight: scale by approximate device pixel size
                        if k == 'stroke_weight':
                            try:
                                sw = float(v)
                                # use average scale to be isotropic when non-square
                                scale = (sx + sy) / 2.0 if (sx and sy) else sx or sy or 1.0
                                args['stroke_weight'] = float(sw) * float(scale)
                            except Exception:
                                args['stroke_weight'] = v
                            continue
                        # text size / generic size keys that represent pixels
                        if k in ('text_size', 'size'):
                            try:
                                ts = float(v)
                                args[k] = float(ts) * sx
                            except Exception:
                                args[k] = v
                            continue
                        # vertices lists: scale numeric vertex coordinates
                        if k == 'vertices' and isinstance(v, (list, tuple)):
                            try:
                                verts: list[Any] = []
                                for item in v:
                                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                                        try:
                                            vx = float(item[0]) * sx
                                            vy = float(item[1]) * sy
                                            verts.append([vx, vy] + list(item[2:]))
                                            continue
                                        except Exception:
                                            verts.append(item)
                                    else:
                                        verts.append(item)
                                args['vertices'] = verts
                            except Exception:
                                args['vertices'] = v
                            continue
                        if k == 'r':
                            # circle radius: scale by device pixel ratio
                            try:
                                vr = float(v)
                                args['r'] = float(vr) * sx
                            except Exception:
                                args['r'] = v
                            continue
                        if k == 'h':
                            try:
                                vh = float(raw_h) if raw_h is not None else float(v)
                                args['h'] = float(vh) * sy
                            except Exception:
                                args['h'] = v
                            continue
                        # default: copy through
                        args[k] = v
                    cmds.append({'op': op, 'args': args, 'meta': {'seq': seq}})

                temp_engine.width = int(round(self.width * sx))
                temp_engine.height = int(round(self.height * sy))
                temp_engine.graphics = types.SimpleNamespace()
                temp_engine.graphics.commands = cmds
                replay_to_image_skia(temp_engine, path)
                try:
                    if self._engine is not None:
                        try:
                            # Record the save request with the recorded ops so
                            # presenters that handle offscreen saves have the
                            # command list available for replay (including
                            # HiDPI scaling). This is best-effort.
                            self._engine.graphics.record('save_offscreen', path=path, backend='skia', width=self.width, height=self.height, ops=list(self._recording))
                        except Exception:
                            # Fall back to a minimal record if the above fails
                            try:
                                self._engine.graphics.record('save_offscreen', path=path, backend='skia')
                            except Exception:
                                pass
                except Exception:
                    pass
                return
            except Exception:
                # Fall through to Pillow fallback below
                pass
        except Exception:
            # skia replayer not available
            pass

        try:
            pil = self.to_pillow()
            if pil is not None:
                pil.save(str(path))
                try:
                    if self._engine is not None:
                        self._engine.graphics.record('save_offscreen', path=path, backend='pillow')
                except Exception:
                    pass
                return
        except Exception:
            pass

        # Last resort: record the save request on the engine for presenters
        if self._engine is not None:
            try:
                g = getattr(self._engine, 'graphics', None)
                if g is not None:
                    g.record('save_offscreen', path=path, backend='none', width=self.width, height=self.height, ops=list(self._recording))
            except Exception:
                pass

    def to_pillow(self):
        """Render the recorded ops to a Pillow Image and return it.

        This is a best-effort rasterization used for headless testing and
        simple exports. It supports background, rect, ellipse and image ops.
        """
        try:
            from PIL import Image, ImageDraw
        except Exception:
            return None

        # Import matrix helpers to apply recorded transforms
        try:
            from core.engine.transforms import identity_matrix, mul_mat
        except Exception:
            # Fallback simple implementations
            def identity_matrix():
                return [1.0, 0.0, 0.0,
                        0.0, 1.0, 0.0,
                        0.0, 0.0, 1.0]

            def mul_mat(a, b):
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

        def apply_mat_to_point(mat, x, y):
            try:
                vx = float(x)
                vy = float(y)
            except Exception:
                return x, y
            nx = mat[0] * vx + mat[1] * vy + mat[2]
            ny = mat[3] * vx + mat[4] * vy + mat[5]
            return nx, ny

        def mat_translate(tx, ty):
            return [1.0, 0.0, float(tx),
                    0.0, 1.0, float(ty),
                    0.0, 0.0, 1.0]

        import math

        def mat_rotate(a):
            c = math.cos(a)
            s = math.sin(a)
            return [c, -s, 0.0,
                    s,  c, 0.0,
                    0.0,0.0,1.0]

        def mat_scale(sx, sy):
            return [float(sx), 0.0, 0.0,
                    0.0, float(sy), 0.0,
                    0.0, 0.0, 1.0]

        def mat_shear_x(a):
            return [1.0, math.tan(a), 0.0,
                    0.0, 1.0,        0.0,
                    0.0, 0.0,        1.0]

        def mat_shear_y(a):
            return [1.0, 0.0,        0.0,
                    math.tan(a), 1.0, 0.0,
                    0.0, 0.0,        1.0]

        img = Image.new('RGBA', (int(self.width), int(self.height)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # maintain a local matrix stack for recorded transforms
        matrix_stack = [identity_matrix()]

        for cmd in self._recording:
            op = cmd.get('op')

            # Handle transform ops by updating matrix_stack
            if op == 'push_matrix':
                matrix_stack.append(list(matrix_stack[-1]))
                continue
            if op == 'pop_matrix':
                if len(matrix_stack) > 1:
                    matrix_stack.pop()
                else:
                    matrix_stack[-1] = identity_matrix()
                continue
            if op == 'reset_matrix':
                matrix_stack[-1] = identity_matrix()
                continue
            if op == 'translate':
                tx = float(cmd.get('x', 0))
                ty = float(cmd.get('y', 0))
                matrix_stack[-1] = mul_mat(matrix_stack[-1], mat_translate(tx, ty))
                continue
            if op == 'rotate':
                ang = float(cmd.get('angle', 0))
                matrix_stack[-1] = mul_mat(matrix_stack[-1], mat_rotate(ang))
                continue
            if op == 'scale':
                sx = float(cmd.get('sx', 1.0))
                sy = float(cmd.get('sy', sx))
                matrix_stack[-1] = mul_mat(matrix_stack[-1], mat_scale(sx, sy))
                continue
            if op == 'shear_x':
                ang = float(cmd.get('angle', 0))
                matrix_stack[-1] = mul_mat(matrix_stack[-1], mat_shear_x(ang))
                continue
            if op == 'shear_y':
                ang = float(cmd.get('angle', 0))
                matrix_stack[-1] = mul_mat(matrix_stack[-1], mat_shear_y(ang))
                continue
            if op == 'apply_matrix':
                m = cmd.get('matrix')
                if isinstance(m, (list, tuple)) and len(m) >= 9:
                    try:
                        mat = [float(v) for v in m[:9]]
                        matrix_stack[-1] = mul_mat(matrix_stack[-1], mat)
                    except Exception:
                        pass
                continue

            # For drawing ops, transform coordinates using current matrix
            top = matrix_stack[-1]

            if op == 'background':
                c = cmd.get('color', (0, 0, 0))
                try:
                    draw.rectangle([(0, 0), (self.width, self.height)], fill=(c[0], c[1], c[2], 255))
                except Exception:
                    pass
                continue

            if op == 'rect':
                x = float(cmd.get('x', 0))
                y = float(cmd.get('y', 0))
                w = float(cmd.get('w', 0))
                h = float(cmd.get('h', 0))
                mode = cmd.get('mode', 'CORNER')
                if mode == 'CENTER':
                    left = x - w / 2.0
                    top = y - h / 2.0
                    right = x + w / 2.0
                    bottom = y + h / 2.0
                else:
                    left = x
                    top = y
                    right = x + w
                    bottom = y + h

                # transform four corners
                p1 = apply_mat_to_point(top, left, top)
                p2 = apply_mat_to_point(top, right, top)
                p3 = apply_mat_to_point(top, right, bottom)
                p4 = apply_mat_to_point(top, left, bottom)
                poly = [p1, p2, p3, p4]
                fill = cmd.get('fill')
                stroke = cmd.get('stroke')
                sw = max(1, int(cmd.get('stroke_weight', 1)))
                try:
                    if fill is not None:
                        draw.polygon(poly, fill=(int(fill[0]), int(fill[1]), int(fill[2]), 255))
                    if stroke is not None and sw > 0:
                        # closed poly outline
                        pts = poly + [poly[0]]
                        draw.line(pts, fill=(int(stroke[0]), int(stroke[1]), int(stroke[2]), 255), width=sw)
                except Exception:
                    pass
                continue

            if op in ('ellipse', 'circle'):
                # For circle, 'r' is radius; for ellipse, w/h are provided
                cx = float(cmd.get('x', 0))
                cy = float(cmd.get('y', 0))
                if op == 'circle':
                    r = float(cmd.get('r', 0))
                    rw = rh = r * 2.0
                else:
                    rw = float(cmd.get('w', 0))
                    rh = float(cmd.get('h', 0))

                # sample ellipse boundary as polygon
                steps = 36
                pts = []
                for i in range(steps):
                    a = (i / float(steps)) * (2.0 * math.pi)
                    px = cx + math.cos(a) * (rw / 2.0)
                    py = cy + math.sin(a) * (rh / 2.0)
                    tx, ty = apply_mat_to_point(top, px, py)
                    pts.append((tx, ty))

                fill = cmd.get('fill')
                stroke = cmd.get('stroke')
                sw = max(1, int(cmd.get('stroke_weight', 1)))
                try:
                    if fill is not None:
                        draw.polygon(pts, fill=(int(fill[0]), int(fill[1]), int(fill[2]), 255))
                    if stroke is not None and sw > 0:
                        draw.line(pts + [pts[0]], fill=(int(stroke[0]), int(stroke[1]), int(stroke[2]), 255), width=sw)
                except Exception:
                    pass
                continue

            if op == 'line':
                try:
                    x1 = float(cmd.get('x1', 0))
                    y1 = float(cmd.get('y1', 0))
                    x2 = float(cmd.get('x2', 0))
                    y2 = float(cmd.get('y2', 0))
                    x1t, y1t = apply_mat_to_point(top, x1, y1)
                    x2t, y2t = apply_mat_to_point(top, x2, y2)
                    stroke = cmd.get('stroke')
                    stroke_alpha = cmd.get('stroke_alpha', None)
                    sw = max(1, int(cmd.get('stroke_weight', 1)))
                    if stroke is not None:
                        try:
                            if stroke_alpha is None:
                                a_val = 255
                            else:
                                try:
                                    a_val = int(max(0, min(1.0, float(stroke_alpha))) * 255)
                                except Exception:
                                    a_val = int(stroke_alpha)
                            color = (int(stroke[0]), int(stroke[1]), int(stroke[2]), a_val)
                            try:
                                draw.line([(x1t, y1t), (x2t, y2t)], fill=color, width=sw)
                            except TypeError:
                                for off in range(sw):
                                    draw.line([(x1t, y1t + off), (x2t, y2t + off)], fill=color)
                        except Exception:
                            pass
                except Exception:
                    pass
                continue

            if op == 'image':
                img_obj = cmd.get('image')
                try:
                    if img_obj is not None and hasattr(img_obj, 'to_pillow'):
                        src = img_obj.to_pillow()
                    else:
                        src = img_obj
                    if src is not None:
                        sx, sy = src.size
                        w = cmd.get('w') or sx
                        h = cmd.get('h') or sy
                        x = cmd.get('x', 0)
                        y = cmd.get('y', 0)
                        # apply translation/scale from matrix to top-left and size
                        tx, ty = apply_mat_to_point(top, x, y)
                        # approximate scale from matrix
                        sx_scale = math.hypot(top[0], top[3])
                        sy_scale = math.hypot(top[1], top[4])
                        try:
                            resized = src.resize((max(1, int(float(w) * sx_scale)), max(1, int(float(h) * sy_scale))))
                            img.paste(resized, (int(tx), int(ty)), resized)
                        except Exception:
                            try:
                                img.paste(src.resize((int(w), int(h))), (int(tx), int(ty)))
                            except Exception:
                                pass
                except Exception:
                    pass
                continue

        return img

    # Context manager support
    def __enter__(self):
        self.begin_draw()
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self.end_draw()
        except Exception:
            pass
