"""PCGraphics: offscreen drawing surface (headless-friendly).

This is a minimal, well-documented implementation intended to provide
the offscreen API used by examples and docs. It records drawing commands
to an engine `graphics` buffer when used in headless mode and provides
the common methods sketches expect: `begin_draw` / `end_draw`, simple
shape helpers, `save`, and basic properties.
"""
from __future__ import annotations

from typing import Any, List, Tuple, Optional


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
        self._fill = (255, 255, 255)
        self._stroke = (0, 0, 0)
        self._stroke_weight = 1
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
                    # Record the offscreen buffer contents as an 'offscreen'
                    # op so presenters can choose how to handle it.
                    g.record('offscreen', width=self.width, height=self.height, ops=list(self._recording))
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
        """Draw a circle with diameter `d` at (x, y).

        Respects the current ellipse mode (CENTER or CORNER-like semantics).
        """
        try:
            self.ellipse(x, y, d, d)
        except Exception:
            self._recording.append({'op': 'ellipse', 'x': float(x), 'y': float(y), 'w': float(d), 'h': float(d), 'fill': self._fill, 'stroke': self._stroke, 'stroke_weight': self._stroke_weight, 'mode': self._ellipse_mode})

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

        # Try to write via Pillow first
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
                    if hasattr(img_obj, 'to_pillow'):
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
