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
                    # Build engine-shaped commands so presenters and the
                    # central replayer receive a consistent format. This
                    # normalizes older top-level keyed ops (the legacy
                    # PCGraphics recording format) into the expected
                    # {'op': name, 'args': {...}} shape.
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

                        # Map common keys through; translate stroke weight
                        # key for consistency with engine naming.
                        for k, v in c.items():
                            if k == 'op':
                                continue
                            # skip background color itself (handled above)
                            if op == 'background' and k == 'color':
                                continue
                            if op == 'stroke_weight' and k == 'w':
                                try:
                                    args['weight'] = float(v)
                                except Exception:
                                    args['weight'] = v
                                continue
                            # copy through most primitive params
                            if k in ('x', 'y', 'w', 'h', 'r', 'fill', 'stroke', 'stroke_weight', 'mode', 'image', 'vertices', 'text_size', 'size'):
                                args[k] = v
                                continue
                            # default passthrough
                            args[k] = v

                        cmds.append({'op': op, 'args': args, 'meta': {'seq': seq}})

                    # Record the normalized offscreen op
                    g.record('offscreen', width=self.width, height=self.height, ops=cmds)
            except Exception:
                pass

    # Simple drawing helpers that record operations
    def background(self, *args):
        # normalize color args like Processing: background(gray) or background(r,g,b)
        col = None
        try:
            if len(args) == 1:
                v = args[0]
                col = (int(v), int(v), int(v))
            elif len(args) >= 3:
                col = (int(args[0]), int(args[1]), int(args[2]))
        except Exception:
            col = (0, 0, 0)
        self._recording.append({'op': 'background', 'color': col})

    def fill(self, r, g=None, b=None):
        if g is None or b is None:
            # grayscale
            self._fill = (int(r), int(r), int(r))
        else:
            self._fill = (int(r), int(g), int(b))
        self._recording.append({'op': 'fill', 'color': self._fill})

    def stroke(self, r, g=None, b=None):
        if g is None or b is None:
            self._stroke = (int(r), int(r), int(r))
        else:
            self._stroke = (int(r), int(g), int(b))
        self._recording.append({'op': 'stroke', 'color': self._stroke})

    def stroke_weight(self, w: float):
        self._stroke_weight = float(w)
        self._recording.append({'op': 'stroke_weight', 'w': float(w)})

    def rect(self, x, y, w, h):
        self._recording.append({'op': 'rect', 'x': float(x), 'y': float(y), 'w': float(w), 'h': float(h), 'fill': self._fill, 'stroke': self._stroke, 'stroke_weight': self._stroke_weight, 'mode': self._rect_mode})

    def ellipse(self, x, y, w, h):
        self._recording.append({'op': 'ellipse', 'x': float(x), 'y': float(y), 'w': float(w), 'h': float(h), 'fill': self._fill, 'stroke': self._stroke, 'stroke_weight': self._stroke_weight, 'mode': self._ellipse_mode})

    def square(self, x, y, s):
        """Draw a square of size `s` at (x, y).

        Respects the current rect mode (CORNER or CENTER).
        """
        try:
            self.rect(x, y, s, s)
        except Exception:
            # best-effort: record the op directly if rect fails
            self._recording.append({'op': 'rect', 'x': float(x), 'y': float(y), 'w': float(s), 'h': float(s), 'fill': self._fill, 'stroke': self._stroke, 'stroke_weight': self._stroke_weight, 'mode': self._rect_mode})

    def circle(self, x, y, d):
        """Draw a circle at (x, y).

        Note: the engine-level `circle()` primitive expects the third
        argument to be a radius (r). To keep PCGraphics consistent with
        the engine API, this records a `circle` op with `r` (radius).

        Respects the current ellipse mode for legacy callers: when the
        mode is 'CENTER' the (x,y) are treated as the center; when the
        mode is 'CORNER' the (x,y) are treated as the top-left corner of
        the bounding box and are converted to a center before recording.
        """
        try:
            # Diameter -> radius conversion for callers that passed a
            # diameter value. If callers were already using radius this
            # will effectively halve/double accordingly; the engine
            # primitive expects radius so record `r` here.
            try:
                dd = float(d)
            except Exception:
                dd = d

            mode = (self._ellipse_mode or 'CENTER').upper()
            if mode == 'CENTER':
                cx = float(x)
                cy = float(y)
            else:
                # CORNER-like semantics: convert top-left to center
                try:
                    cx = float(x) + (dd / 2.0)
                    cy = float(y) + (dd / 2.0)
                except Exception:
                    cx = float(x)
                    cy = float(y)

            # Treat the provided value as a radius to match the engine API
            # (engine.circle takes radius). This makes PCGraphics and the
            # main canvas consistent when callers pass the same number.
            # Convert diameter -> radius to record engine-style `circle(r)`
            r = float(dd) / 2.0
            self._recording.append({'op': 'circle', 'x': cx, 'y': cy, 'r': r, 'fill': self._fill, 'stroke': self._stroke, 'stroke_weight': self._stroke_weight})
        except Exception:
            # Fallback to recording an ellipse (legacy path)
            try:
                self._recording.append({'op': 'ellipse', 'x': float(x), 'y': float(y), 'w': float(d), 'h': float(d), 'fill': self._fill, 'stroke': self._stroke, 'stroke_weight': self._stroke_weight, 'mode': self._ellipse_mode})
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

        img = Image.new('RGBA', (int(self.width), int(self.height)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        for cmd in self._recording:
            op = cmd.get('op')
            if op == 'background':
                c = cmd.get('color', (0, 0, 0))
                try:
                    draw.rectangle([(0, 0), (self.width, self.height)], fill=(c[0], c[1], c[2], 255))
                except Exception:
                    pass
            elif op == 'rect':
                x = cmd.get('x', 0)
                y = cmd.get('y', 0)
                w = cmd.get('w', 0)
                h = cmd.get('h', 0)
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
                fill = cmd.get('fill')
                stroke = cmd.get('stroke')
                sw = max(1, int(cmd.get('stroke_weight', 1)))
                try:
                    if fill is not None:
                        draw.rectangle([left, top, right, bottom], fill=(fill[0], fill[1], fill[2], 255))
                    if stroke is not None and sw > 0:
                        # draw outline separately if stroke present
                        for i in range(sw):
                            draw.rectangle([left - i, top - i, right + i, bottom + i], outline=(stroke[0], stroke[1], stroke[2], 255))
                except Exception:
                    pass
            elif op == 'ellipse':
                x = cmd.get('x', 0)
                y = cmd.get('y', 0)
                w = cmd.get('w', 0)
                h = cmd.get('h', 0)
                mode = cmd.get('mode', 'CENTER')
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
                fill = cmd.get('fill')
                stroke = cmd.get('stroke')
                sw = max(1, int(cmd.get('stroke_weight', 1)))
                try:
                    if fill is not None:
                        draw.ellipse([left, top, right, bottom], fill=(fill[0], fill[1], fill[2], 255))
                    if stroke is not None and sw > 0:
                        for i in range(sw):
                            draw.ellipse([left - i, top - i, right + i, bottom + i], outline=(stroke[0], stroke[1], stroke[2], 255))
                except Exception:
                    pass
            elif op == 'image':
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
                        try:
                            img.paste(src.resize((int(w), int(h))), (int(x), int(y)), src.resize((int(w), int(h))))
                        except Exception:
                            try:
                                img.paste(src.resize((int(w), int(h))), (int(x), int(y)))
                            except Exception:
                                pass
                except Exception:
                    pass

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
