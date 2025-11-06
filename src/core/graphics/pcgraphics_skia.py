"""GPU-backed PCGraphics using skia-python and an OpenGL backend.

This class attempts to create a GPU Skia surface (GrDirectContext +
backend render target) bound to its own GL texture/FBO so callers get an
independent offscreen surface that can be drawn into and snapshot.

If the GPU path fails it falls back to a CPU Skia raster surface so the
API remains usable in headless/test environments.
"""
from __future__ import annotations

from typing import Any, Optional, List


class PCGraphicsSkia:
    def __init__(self, width: int, height: int, engine: Optional[Any] = None, force_cpu: bool = False):
        self.width = int(width)
        self.height = int(height)
        self._engine = engine
        self._recording: List[dict] = []
        self._in_draw = False
        # Per-surface default state (keep API similar to CPU PCGraphics)
        self._fill: tuple[int, int, int] = (255, 255, 255)
        self._stroke: tuple[int, int, int] = (0, 0, 0)
        self._stroke_weight: float = 1.0
        # drawing modes
        self._rect_mode = 'CORNER'
        self._ellipse_mode = 'CENTER'
        # backing GL ids (may be None if using CPU fallback)
        self._tex: Optional[int] = None
        self._fbo: Optional[int] = None
        self._gr_ctx: Optional[Any] = None
        self._surf: Optional[Any] = None

        # Try to create a GPU-backed Skia surface (unless caller forces CPU).
        # In headless or CI environments attempting to create a GL context
        # can hang or fail; callers may set `force_cpu=True` to skip GPU setup
        # and use the CPU raster Skia surface instead.
        if not force_cpu:
            try:
                import skia
                from pyglet import gl

                # Create or reuse a GrDirectContext bound to current GL context
                try:
                    ctx = skia.GrDirectContext.MakeGL()
                except Exception:
                    ctx = None

                if ctx is not None:
                    # Create GL texture
                    try:
                        tex = gl.GLuint()
                        gl.glGenTextures(1, tex)
                        self._tex = int(tex.value)
                        gl.glBindTexture(gl.GL_TEXTURE_2D, self._tex)
                        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
                        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
                        # allocate storage
                        try:
                            # Prefer RGBA8
                            internal = int(gl.GL_RGBA8)
                        except Exception:
                            internal = int(gl.GL_RGBA)
                        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, internal, int(self.width), int(self.height), 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
                        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

                        # create FBO and attach
                        fbo = gl.GLuint()
                        gl.glGenFramebuffers(1, fbo)
                        self._fbo = int(fbo.value)
                        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._fbo)
                        try:
                            gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, int(self._tex), 0)
                        except Exception:
                            # some platforms expose different symbol signatures
                            try:
                                gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, int(self._tex), 0)
                            except Exception:
                                pass
                        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

                        # Create Skia backend render target for the texture
                        fb_fmt = None
                        try:
                            fb_fmt = int(gl.GL_RGBA8)
                        except Exception:
                            try:
                                fb_fmt = int(gl.GL_RGBA)
                            except Exception:
                                fb_fmt = 0

                        fb_info = skia.GrGLFramebufferInfo(int(self._fbo or 0), int(fb_fmt))
                        backend_rt = skia.GrBackendRenderTarget(int(self.width), int(self.height), 0, 0, fb_info)
                        surf = skia.Surface.MakeFromBackendRenderTarget(
                            ctx,
                            backend_rt,
                            skia.kBottomLeft_GrSurfaceOrigin,
                            skia.kRGBA_8888_ColorType,
                            skia.ColorSpace.MakeSRGB(),
                        )
                        if surf is not None:
                            self._gr_ctx = ctx
                            self._surf = surf
                    except Exception:
                        # On any GL/Skia error fall back below
                        try:
                            self._tex = None
                            self._fbo = None
                        except Exception:
                            pass

            except Exception:
                # skia or pyglet not available; will attempt CPU raster fallback
                pass

        # CPU skia fallback if GPU surface creation failed
        if getattr(self, '_surf', None) is None:
            try:
                import skia

                try:
                    self._surf = skia.Surface.MakeRasterN32Premul(int(self.width), int(self.height))
                except Exception:
                    self._surf = None
            except Exception:
                self._surf = None

    def begin_draw(self):
        self._in_draw = True
        self._recording.clear()

    def end_draw(self):
        self._in_draw = False
        # If we have a Skia surface, replay recorded ops directly into it
        if self._surf is not None:
            try:
                canvas = self._surf.getCanvas()
                # Delegate to the central replayer which understands our ops
                try:
                    from core.io.replay_to_skia_impl import replay_to_skia_canvas

                    # The central replayer expects commands in the shape
                    # {'op': ..., 'args': {...}} (this is what the engine
                    # presenter's flattened commands look like). Older
                    # PCGraphics implementations record ops with keys at
                    # the top level (e.g. {'op': 'rect', 'x':..., 'w':...}).
                    # Normalize our internal recording to the expected
                    # shape so replay_to_skia_canvas can read args via
                    # cmd.get('args', {}). This preserves compatibility
                    # with the engine-style saver used elsewhere.
                    cmds = []
                    for c in list(self._recording):
                        try:
                            op = c.get('op')
                        except Exception:
                            op = None

                        # Precompute possible center->corner conversion when
                        # callers used CENTER mode. This mirrors the logic in
                        # save() so the live replay path matches CPU behaviour.
                        raw_x = c.get('x')
                        raw_y = c.get('y')
                        raw_w = c.get('w')
                        raw_h = c.get('h')
                        mode_val = (c.get('mode') or '').upper()
                        if mode_val == 'CENTER' and raw_x is not None and raw_y is not None and raw_w is not None and raw_h is not None:
                            try:
                                raw_x = float(raw_x) - float(raw_w) / 2.0
                                raw_y = float(raw_y) - float(raw_h) / 2.0
                            except Exception:
                                pass

                        args = {}
                        try:
                            for k, v in c.items():
                                if k == 'op':
                                    continue
                                # background handled below
                                args[k] = v
                        except Exception:
                            args = {}

                        # Normalize background color tuple into r/g/b keys
                        if op == 'background' and 'color' in args:
                            col = args.pop('color')
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

                        # Prefer converted raw_x/raw_y when CENTER->CORNER
                        if 'x' in args:
                            try:
                                if raw_x is not None:
                                    args['x'] = float(raw_x)
                                else:
                                    args['x'] = float(args.get('x', 0))
                            except Exception:
                                pass
                        if 'y' in args:
                            try:
                                if raw_y is not None:
                                    args['y'] = float(raw_y)
                                else:
                                    args['y'] = float(args.get('y', 0))
                            except Exception:
                                pass
                        if 'w' in args and raw_w is not None:
                            try:
                                args['w'] = float(raw_w)
                            except Exception:
                                pass
                        if 'h' in args and raw_h is not None:
                            try:
                                args['h'] = float(raw_h)
                            except Exception:
                                pass

                        cmds.append({'op': op, 'args': args})

                    replay_to_skia_canvas(cmds, canvas)
                except Exception:
                    # last resort: record into engine so presenter can pick it up
                    try:
                        if self._engine is not None:
                            g = getattr(self._engine, 'graphics', None)
                            if g is not None:
                                g.record('offscreen', width=self.width, height=self.height, ops=list(self._recording))
                    except Exception:
                        pass
                try:
                    # flush/skia submit if we have GPU context
                    if self._gr_ctx is not None:
                        try:
                            if hasattr(self._gr_ctx, 'flush'):
                                self._gr_ctx.flush()
                            if hasattr(self._gr_ctx, 'submit'):
                                self._gr_ctx.submit()
                        except Exception:
                            pass
                except Exception:
                    pass
            except Exception:
                # fallback: record on engine
                try:
                    if self._engine is not None:
                        g = getattr(self._engine, 'graphics', None)
                        if g is not None:
                            g.record('offscreen', width=self.width, height=self.height, ops=list(self._recording))
                except Exception:
                    pass
        else:
            # No Skia surface: record for presenters or fall back to core PCGraphics
            try:
                if self._engine is not None:
                    g = getattr(self._engine, 'graphics', None)
                    if g is not None:
                        g.record('offscreen', width=self.width, height=self.height, ops=list(self._recording))
            except Exception:
                pass

    # Recording helpers (same shape as the CPU PCGraphics)
    def background(self, *args):
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
            col = (int(r), int(r), int(r))
        else:
            col = (int(r), int(g), int(b))
        # Update internal fill state so subsequent shape recordings include
        # the correct fill color (mirror CPU PCGraphics behaviour).
        try:
            self._fill = col
        except Exception:
            pass
        self._recording.append({'op': 'fill', 'color': col})

    def stroke(self, r, g=None, b=None):
        if g is None or b is None:
            col = (int(r), int(r), int(r))
        else:
            col = (int(r), int(g), int(b))
        # Update internal stroke state so subsequent shape recordings include
        # the correct stroke color (mirror CPU PCGraphics behaviour).
        try:
            self._stroke = col
        except Exception:
            pass
        self._recording.append({'op': 'stroke', 'color': col})

    def stroke_weight(self, w: float):
        # Update internal stroke weight state so shapes pick up the value
        try:
            self._stroke_weight = float(w)
        except Exception:
            pass
        self._recording.append({'op': 'stroke_weight', 'w': float(w)})

    def rect(self, x, y, w, h):
        # Record rect with current fill/stroke state and mode (mirror PCGraphics)
        self._recording.append({
            'op': 'rect',
            'x': float(x),
            'y': float(y),
            'w': float(w),
            'h': float(h),
            'fill': self._fill,
            'stroke': self._stroke,
            'stroke_weight': self._stroke_weight,
            'mode': self._rect_mode,
        })

    def ellipse(self, x, y, w, h):
        # Record ellipse with current fill/stroke and mode
        self._recording.append({
            'op': 'ellipse',
            'x': float(x),
            'y': float(y),
            'w': float(w),
            'h': float(h),
            'fill': self._fill,
            'stroke': self._stroke,
            'stroke_weight': self._stroke_weight,
            'mode': self._ellipse_mode,
        })

    def square(self, x, y, s):
        """Draw a square of size `s` at (x, y)."""
        try:
            self.rect(x, y, s, s)
        except Exception:
            # Fallback: ensure same fill/stroke/mode are recorded
            self._recording.append({
                'op': 'rect',
                'x': float(x),
                'y': float(y),
                'w': float(s),
                'h': float(s),
                'fill': self._fill,
                'stroke': self._stroke,
                'stroke_weight': self._stroke_weight,
                'mode': self._rect_mode,
            })

    def circle(self, x, y, d):
        """Record a circle op using radius `r` (compatible with engine.circle).

        PCGraphics records circle ops with `r` (radius). We accept a
        diameter-like argument and convert to radius for recording so
        the central replayer sees `circle` ops like the CPU path.
        """
        try:
            dd = float(d)
        except Exception:
            dd = d
        mode = (getattr(self, '_ellipse_mode', 'CENTER') or 'CENTER').upper()
        if mode == 'CENTER':
            cx = float(x)
            cy = float(y)
        else:
            try:
                cx = float(x) + (dd / 2.0)
                cy = float(y) + (dd / 2.0)
            except Exception:
                cx = float(x)
                cy = float(y)

        try:
            r = float(dd) / 2.0
            self._recording.append({'op': 'circle', 'x': cx, 'y': cy, 'r': r, 'fill': self._fill, 'stroke': self._stroke, 'stroke_weight': self._stroke_weight})
        except Exception:
            try:
                self._recording.append({'op': 'ellipse', 'x': float(x), 'y': float(y), 'w': float(d), 'h': float(d)})
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

    def image(self, img, x, y, w=None, h=None):
        self._recording.append({'op': 'image', 'image': img, 'x': float(x), 'y': float(y), 'w': (float(w) if w is not None else None), 'h': (float(h) if h is not None else None)})

    def save(self, path: str):
        # Prefer using the centralized Skia replayer so offscreen saves
        # match engine.save_frame output when possible.
        try:
            from core.io.skia_replayer import replay_to_image_skia
            import types

            try:
                temp_engine = types.SimpleNamespace()
                # Determine HiDPI scale from bound engine/presenter if available
                sx = sy = 1.0
                try:
                    if self._engine is not None:
                        pres = getattr(self._engine, '_presenter', None)
                        if pres is not None:
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

                cmds = []
                seq = 0
                for c in list(self._recording):
                    seq += 1
                    op = c.get('op')
                    args: dict[str, Any] = {}
                    # handle background color mapping
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

                    # Precompute possible center->corner conversion
                    raw_x = c.get('x')
                    raw_y = c.get('y')
                    raw_w = c.get('w')
                    raw_h = c.get('h')
                    mode_val = (c.get('mode') or '').upper()
                    if mode_val == 'CENTER' and raw_x is not None and raw_y is not None and raw_w is not None and raw_h is not None:
                        try:
                            raw_x = float(raw_x) - float(raw_w) / 2.0
                            raw_y = float(raw_y) - float(raw_h) / 2.0
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
                        if k == 'x':
                            try:
                                vx = float(raw_x) if raw_x is not None else float(v)
                                args['x'] = float(vx) * sx
                                continue
                            except Exception:
                                pass
                            if isinstance(v, (int, float)):
                                args['x'] = float(v) * sx
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
                        if k == 'w':
                            try:
                                vw = float(raw_w) if raw_w is not None else float(v)
                                args['w'] = float(vw) * sx
                            except Exception:
                                args['w'] = v
                            continue
                        if k == 'h':
                            try:
                                vh = float(raw_h) if raw_h is not None else float(v)
                                args['h'] = float(vh) * sy
                            except Exception:
                                args['h'] = v
                            continue
                        args[k] = v
                    cmds.append({'op': op, 'args': args, 'meta': {'seq': seq}})

                temp_engine.width = int(round(self.width * sx))
                temp_engine.height = int(round(self.height * sy))
                temp_engine.graphics = types.SimpleNamespace()
                temp_engine.graphics.commands = cmds
                replay_to_image_skia(temp_engine, path)
                try:
                    if self._engine is not None:
                        g = getattr(self._engine, 'graphics', None)
                        if g is not None:
                            g.record('save_offscreen', path=path, backend='skia', width=self.width, height=self.height, ops=list(self._recording))
                except Exception:
                    pass
                return
            except Exception:
                pass
        except Exception:
            pass

        # Try to snapshot via Skia/Pillow fallback
        try:
            pil = self.to_pillow()
            if pil is not None:
                pil.save(path)
                return
        except Exception:
            pass

        # Last resort: record the save request on the engine for presenters
        # to handle later.
        try:
            if self._engine is not None:
                g = getattr(self._engine, 'graphics', None)
                if g is not None:
                    g.record('save_offscreen', path=path, backend='none', width=self.width, height=self.height, ops=list(self._recording))
        except Exception:
            pass

    def to_pillow(self):
        try:
            from PIL import Image
            from io import BytesIO
        except Exception:
            return None

        if self._surf is None:
            return None

        try:
            img = self._surf.makeImageSnapshot()
            if img is None:
                return None
            data = img.encodeToData()
            if data is None:
                return None
            # prefer bytes-like API
            if hasattr(data, 'toBytes'):
                b = data.toBytes()
            elif hasattr(data, 'tobytes'):
                b = data.tobytes()
            else:
                b = bytes(data)

            # Try to decode via PIL (PNG/JPEG encoded data) first, then raw RGBA fallback
            try:
                return Image.open(BytesIO(b)).convert('RGBA')
            except Exception:
                try:
                    return Image.frombuffer('RGBA', (int(self.width), int(self.height)), b, 'raw', 'RGBA', 0, 1)
                except Exception:
                    return None
        except Exception:
            return None

    def pixels(self):
        class _CM:
            def __init__(self, parent):
                self._parent = parent

            def __enter__(self):
                return self._parent.to_pillow()

            def __exit__(self, exc_type, exc, tb):
                return False

        return _CM(self)

    # Context manager
    def __enter__(self):
        self.begin_draw()
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self.end_draw()
        except Exception:
            pass
