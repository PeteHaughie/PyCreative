from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..impl import Engine


class SimpleSketchAPI:
    """Lightweight object passed to sketches as `this`.

    It offers convenience methods that delegate to the Engine's API registry
    and control lifecycle behaviour (size/no_loop/loop/redraw/save_frame).
    """

    def __init__(self, engine: 'Engine'):
        self._engine = engine
        # Cache frequently-used engine functions as instance attributes to
        # avoid the per-call registry lookup overhead when sketches call
        # these in tight inner loops (e.g., per-pixel noise sampling).
        try:
            fn_noise = self._engine.api.get('noise')
            if fn_noise:
                # Attach as an attribute to shadow the method lookup and
                # provide a fast, direct call path.
                try:
                    setattr(self, 'noise', fn_noise)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            fn_noise_seed = self._engine.api.get('noise_seed')
            if fn_noise_seed:
                try:
                    setattr(self, 'noise_seed', fn_noise_seed)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            fn_noise_detail = self._engine.api.get('noise_detail')
            if fn_noise_detail:
                try:
                    setattr(self, 'noise_detail', fn_noise_detail)
                except Exception:
                    pass
        except Exception:
            pass
        # expose PCVector constructor to sketches as `this.pcvector`
        try:
            from core.math import PCVector  # local import to avoid top-level cost
            # provide a small factory so sketches can do `v = this.pcvector()`
            # We wrap the raw PCVector class in a thin object that acts as a
            # constructor but also exposes Processing-style non-mutating helpers
            # as methods (sub/add/mult/div). This keeps examples that call
            # `this.pcvector.sub(a, b)` working and avoids accidental mutation
            # when a non-mutating semantics is expected.
            class _PCVectorFactory:
                def __call__(self, x=0.0, y=0.0):
                    return PCVector(x, y)

                # expose non-mutating helpers that return new PCVector
                def sub(self, a, b):
                    return PCVector.sub_vec(a, b)

                def add(self, a, b):
                    return PCVector.add_vec(a, b)

                def mult(self, a, n):
                    return PCVector.mult_vec(a, n)

                def div(self, a, n):
                    return PCVector.div_vec(a, n)

                # Expose common static/helpers from PCVector for sketches that
                # call `this.pcvector.random2d()` or `this.pcvector.from_angle()`.
                def random2d(self, magnitude: float = 1.0):
                    try:
                        return PCVector.random2d(float(magnitude))
                    except Exception:
                        return PCVector.from_angle(0.0, float(magnitude))

                def from_angle(self, angle: float, magnitude: float = 1.0):
                    try:
                        return PCVector.from_angle(float(angle), float(magnitude))
                    except Exception:
                        return PCVector(0.0, 0.0)

            self.pcvector: Any = _PCVectorFactory()
            # Expose Processing-style shape mode constants so sketches can
            # reference `this.CENTER`, `this.CORNER`, etc.
            try:
                setattr(self, 'CENTER', 'CENTER')
                setattr(self, 'CORNER', 'CORNER')
                setattr(self, 'CORNERS', 'CORNERS')
                setattr(self, 'RADIUS', 'RADIUS')
            except Exception:
                pass
            # Expose common math helpers at the sketch-level as documented
            # (e.g., this.lerp, this.map, this.dist, etc.). We expose a
            # conservative set matching docs/api/math/calculation.
            try:
                import core.math as _math
                # Only export math helpers that have API docs under
                # docs/api/math/calculation/ — keep the public surface limited to
                # documented functions.
                for _name in (
                    'abs', 'ceil', 'floor', 'constrain', 'dist', 'lerp', 'mag', 'map',
                    'sq', 'sqrt', 'pow', 'max', 'min', 'round', 'exp', 'log', 'norm'
                ):
                    if hasattr(_math, _name):
                        try:
                            setattr(self, _name, getattr(_math, _name))
                        except Exception:
                            pass
            except Exception:
                # If math module cannot be imported, silently continue; tests
                # will skip or fail intentionally.
                pass
            # Expose common math constants (PI, TWO_PI, HALF_PI, etc.) so
            # examples that reference `this.TWO_PI` or `this.PI` work.
            try:
                from core.constants import PI as _PI, TWO_PI as _TWO_PI, HALF_PI as _HALF_PI, QUARTER_PI as _QUARTER_PI, TAU as _TAU
                try:
                    setattr(self, 'PI', _PI)
                    setattr(self, 'TWO_PI', _TWO_PI)
                    setattr(self, 'HALF_PI', _HALF_PI)
                    setattr(self, 'QUARTER_PI', _QUARTER_PI)
                    setattr(self, 'TAU', _TAU)
                except Exception:
                    pass
            except Exception:
                pass
        except Exception:
            # if math isn't available for some reason, expose a minimal fallback
            class _FallbackVec:
                def __init__(self, x=0, y=0):
                    self.x = x
                    self.y = y

            self.pcvector = _FallbackVec

    def rect(self, x, y, w, h, **kwargs):
        fn = self._engine.api.get('rect')
        if fn:
            return fn(x, y, w, h, **kwargs)

    # Expose noise API helpers on the SimpleSketchAPI so class-based
    # sketches receive engine-backed implementations when methods are
    # attached to sketch instances during Engine normalization.
    def noise(self, *args, **kwargs):
        try:
            fn = self._engine.api.get('noise')
            if fn:
                return fn(*args, **kwargs)
        except Exception:
            pass
        # fallback behaviour: raise or return 0.0
        try:
            return 0.0
        except Exception:
            return 0.0

    def noise_seed(self, *args, **kwargs):
        try:
            fn = self._engine.api.get('noise_seed')
            if fn:
                return fn(*args, **kwargs)
        except Exception:
            pass
        return None

    def noise_detail(self, *args, **kwargs):
        try:
            fn = self._engine.api.get('noise_detail')
            if fn:
                return fn(*args, **kwargs)
        except Exception:
            pass
        return None

    def noise_field(self, *args, **kwargs):
        """Compute a vectorized noise field. This delegates to the
        core.random.ops.noise_field implementation when available."""
        try:
            # Prefer registering via engine API if present
            fn = self._engine.api.get('noise_field')
            if fn:
                return fn(*args, **kwargs)
        except Exception:
            pass
        try:
            # Fallback: import directly
            from core.random import ops as _ops

            return _ops.noise_field(self._engine, *args, **kwargs)
        except Exception:
            return None

    @property
    def width(self) -> int:
        """Current sketch width (reads from the engine)."""
        return int(getattr(self._engine, 'width', 0))

    @property
    def height(self) -> int:
        """Current sketch height (reads from the engine)."""
        return int(getattr(self._engine, 'height', 0))

    # lifecycle and environment helpers exposed to sketches
    def size(self, w: int, h: int):
        """Set sketch size (should be called in setup())."""
        self._engine._set_size(w, h)

    def window_title(self, title: str):
        """Set window title (if applicable)."""
        try:
            # Persist the requested title on the engine so calls made during
            # setup (before a window exists) are applied once the window is
            # created.
            try:
                setattr(self._engine, '_pending_window_title', str(title))
            except Exception:
                pass

            win = getattr(self._engine, '_window', None)
            if win is not None:
                win.set_caption(str(title))
        except Exception:
            # Non-fatal: if pyglet isn't available or call fails, continue
            pass

    def frame_rate(self, n: int):
        """Set frame rate. Use -1 for unrestricted."""
        try:
            self._engine.frame_rate = int(n)
        except Exception:
            raise TypeError('frame_rate expects an integer')

    def background(self, *args):
        """Delegate to the shared background implementation in core.color."""
        try:
            from core.color.background import set_background
            return set_background(self._engine, *args)
        except Exception:
            # Avoid raising unexpected errors during sketches — surface-level
            # type/argument errors should still propagate, but other failures
            # are non-fatal.
            raise

    def no_loop(self):
        self._engine._no_loop()

    def loop(self):
        self._engine._loop()

    def redraw(self):
        self._engine._redraw()

    def save_frame(self, path: str):
        self._engine._save_frame(path)

    # Image helpers
    def load_image(self, path: str, extension: Optional[str] = None):
        try:
            fn = self._engine.api.get('load_image')
            if fn:
                return fn(path, extension)
        except Exception:
            pass
        # fallback: attempt to call core.image directly
        try:
            from core.image import load_image as _li

            return _li(path, extension)
        except Exception:
            return None

    def request_image(self, path: str, extension: Optional[str] = None):
        try:
            fn = self._engine.api.get('request_image')
            if fn:
                return fn(path, extension)
        except Exception:
            pass
        try:
            from core.image import request_image as _ri

            return _ri(path, extension)
        except Exception:
            return None

    def create_image(self, w: int, h: int):
        try:
            fn = self._engine.api.get('create_image')
            if fn:
                return fn(w, h)
        except Exception:
            pass
        try:
            from core.image import create_image as _ci

            return _ci(w, h)
        except Exception:
            return None

    def image(self, img, x, y, w=None, h=None, mode='CORNER', **kwargs):
        """Draw or record an image. Accepts a PCImage-like object or a path.

        This delegates to a registered 'image' API when available, otherwise
        records an 'image' op on the engine graphics buffer so headless and
        replay paths work consistently.
        """
        try:
            fn = self._engine.api.get('image')
            if fn:
                return fn(img, x, y, w, h, mode=mode, **kwargs)
        except Exception:
            pass
        # Fallback: record the image draw operation on the graphics buffer
        args = {'image': img, 'x': float(x), 'y': float(y), 'mode': mode}
        # Snapshot raw image bytes at record time when possible. This avoids
        # races where the recorded PCImage object is mutated later and the
        # replayer sees stale/uninitialized data. Use a best-effort approach
        # and attach bytes/mode/size to the recorded args for replay.
        try:
            pil = None
            # Accept either a PCImage-like object with to_pillow() or a raw PIL Image
            if hasattr(img, 'to_pillow'):
                try:
                    pil = img.to_pillow()
                except Exception:
                    pil = None
            else:
                # maybe it's already a Pillow Image
                try:
                    from PIL import Image as _PILImage
                    if isinstance(img, _PILImage.Image):
                        pil = img
                except Exception:
                    pil = None

            if pil is not None:
                try:
                    if getattr(pil, 'mode', None) != 'RGBA':
                        pil = pil.convert('RGBA')
                    raw = pil.tobytes()
                    args['image_bytes'] = raw
                    args['image_mode'] = 'RGBA'
                    args['image_size'] = tuple(pil.size)
                except Exception:
                    # best-effort: don't fail recording if snapshotting fails
                    pass
        except Exception:
            pass
        if w is not None:
            try:
                args['w'] = float(w)
            except Exception:
                args['w'] = w
        if h is not None:
            try:
                args['h'] = float(h)
            except Exception:
                args['h'] = h
        try:
            return self._engine.graphics.record('image', **args)
        except Exception:
            return None

    def image_mode(self, mode: str):
        """Set the image drawing mode (e.g., 'CENTER', 'CORNER', 'CORNERS').

        This updates engine state so subsequent `image()` calls and
        replayers respect the chosen mode.
        """
        try:
            # Update engine state
            try:
                self._engine.image_mode = str(mode)
            except Exception:
                pass
            # If the engine provided a recorder for image_mode, call it
            fn = self._engine.api.get('image_mode')
            if fn:
                try:
                    return fn(mode)
                except Exception:
                    pass
        except Exception:
            pass
        return None

    def line(self, x1, y1, x2, y2, **kwargs):
        fn = self._engine.api.get('line')
        if fn:
            return fn(x1, y1, x2, y2, **kwargs)

    def circle(self, x, y, r, **kwargs):
        fn = self._engine.api.get('circle')
        if fn:
            return fn(x, y, r, **kwargs)

    def ellipse(self, x, y, w, h=None, **kwargs):
        # ellipse(w,h) overload: if h is None, treat as circle-like diameter
        if h is None:
            h = w
        fn = self._engine.api.get('ellipse')
        if fn:
            return fn(x, y, w, h, **kwargs)

    def point(self, x, y, **kwargs):
        fn = self._engine.api.get('point')
        if fn:
            return fn(x, y, **kwargs)

    # shape recording helpers
    def begin_shape(self, mode: str = 'POLYGON'):
        fn = self._engine.api.get('begin_shape')
        if fn:
            return fn(mode)

    def vertex(self, x, y):
        fn = self._engine.api.get('vertex')
        if fn:
            return fn(x, y)

    def end_shape(self, close: bool = False):
        fn = self._engine.api.get('end_shape')
        if fn:
            return fn(close)

    # new drawing state helpers
    def fill(self, *args):
        """Set fill color respecting color_mode (RGB or HSB). Delegates to core.color.fill."""
        from core.color.fill import set_fill
        # Update engine state
        set_fill(self._engine, *args)
        # If the engine provided a recorder for 'fill', call it to record the command
        try:
            fn = self._engine.api.get('fill')
            if fn:
                return fn(self._engine.fill_color)
        except Exception:
            pass

    def tint(self, *args):
        """Set a global tint color for image draws. Accepts a color tuple or None to clear.

        This mirrors Processing's tint() which multiplies image colors on draw.
        We record a 'tint' op on the graphics buffer so replayers can apply it.
        """
        try:
            # Simple parsing: accept either a single tuple/list or individual components
            if len(args) == 0:
                c = None
            elif len(args) == 1:
                c = args[0]
            else:
                c = tuple(args)
            # Persist on engine for direct queries
            try:
                setattr(self._engine, 'tint_color', c)
            except Exception:
                pass
            # If an engine-registered 'tint' handler exists, call it
            try:
                fn = self._engine.api.get('tint')
                if fn:
                    return fn(c)
            except Exception:
                pass
            # Fallback: record the tint op on the graphics buffer
            try:
                return self._engine.graphics.record('tint', color=c)
            except Exception:
                return None
        except Exception:
            return None

    def stroke(self, *args):
        """Set stroke color respecting color_mode (RGB or HSB). Delegates to core.color.stroke."""
        from core.color.stroke import set_stroke
        set_stroke(self._engine, *args)
        try:
            fn = self._engine.api.get('stroke')
            if fn:
                return fn(self._engine.stroke_color)
        except Exception:
            pass

    def color_mode(self, mode: str, *max_values):
        """Set the engine's color mode and optional component maxima.

        Usage examples:
            this.color_mode('RGB')
            this.color_mode('HSB', 360, 100, 100)

        The optional numeric `max_values` are stored on `engine.color_mode_max`
        and used by high-level parsing helpers to normalize inputs into the
        canonical 0..1 ranges used by the pure converters.
        """
        try:
            m = str(mode).upper()
        except Exception:
            raise TypeError('color_mode expects a string')

        if m in ('RGB',):
            setattr(self._engine, 'color_mode', 'RGB')
            # Default RGB maxima: 255 per channel
            if len(max_values) == 0:
                setattr(self._engine, 'color_mode_max', (255.0, 255.0, 255.0))
            else:
                setattr(self._engine, 'color_mode_max', tuple(float(x) for x in max_values))
            return
        if m in ('HSB', 'HSV'):
            setattr(self._engine, 'color_mode', 'HSB')
            # Processing defaults: H in [0,360], S in [0,100], B in [0,100]
            if len(max_values) == 0:
                setattr(self._engine, 'color_mode_max', (360.0, 100.0, 100.0))
            else:
                setattr(self._engine, 'color_mode_max', tuple(float(x) for x in max_values))
            return

        raise ValueError(f'unsupported color mode: {mode}')

    def no_fill(self):
        """Disable filling geometry."""
        try:
            fn = self._engine.api.get('no_fill')
            if fn:
                return fn()
        except Exception:
            pass
        # Fallback: set engine state
        try:
            self._engine.fill_color = None
        except Exception:
            pass

    def no_stroke(self):
        """Disable drawing of stroke (outline)."""
        try:
            fn = self._engine.api.get('no_stroke')
            if fn:
                return fn()
        except Exception:
            pass
        try:
            self._engine.stroke_color = None
        except Exception:
            pass

    def stroke_weight(self, w: int):
        self._engine.stroke_weight = int(w)

    def stroke_cap(self, cap):
        """Set stroke cap style (PROJECT, SQUARE, ROUND)."""
        try:
            fn = self._engine.api.get('stroke_cap')
            if fn:
                return fn(cap)
        except Exception:
            pass

    def stroke_join(self, join):
        """Set stroke join style (MITER, BEVEL, ROUND)."""
        try:
            fn = self._engine.api.get('stroke_join')
            if fn:
                return fn(join)
        except Exception:
            pass

    def random(self, *args):
        """Return a random float using the engine's RNG. See docs for overloads."""
        try:
            fn = self._engine.api.get('random')
            if fn:
                return fn(*args)
        except Exception:
            pass
        raise RuntimeError('random() API not available')

    def uniform(self, low, high):
        """Return a random float between low and high using the engine's RNG."""
        try:
            fn = self._engine.api.get('uniform')
            if fn:
                return fn(low, high)
        except Exception:
            pass
        raise RuntimeError('uniform() API not available')

    def random_gaussian(self):
        """Return a Gaussian-distributed value using the engine RNG."""
        try:
            fn = self._engine.api.get('random_gaussian')
            if fn:
                return fn()
        except Exception:
            pass
        raise RuntimeError('random_gaussian() API not available')

    def random_seed(self, seed):
        """Seed the engine's RNG for deterministic sequences."""
        try:
            fn = self._engine.api.get('random_seed')
            if fn:
                return fn(seed)
        except Exception:
            pass
        raise RuntimeError('random_seed() API not available')

    def square(self, x, y, size, **kwargs):
        # delegate to rect with equal width/height; also forward drawing state
        fill = kwargs.pop('fill', None)
        stroke = kwargs.pop('stroke', None)
        sw = kwargs.pop('stroke_weight', None)
        # prefer explicit args, otherwise use engine state
        if fill is None:
            fill = self._engine.fill_color
        if stroke is None:
            stroke = self._engine.stroke_color
        if sw is None:
            sw = self._engine.stroke_weight
        fn = self._engine.api.get('rect')
        if fn:
            return fn(x, y, size, size, fill=fill, stroke=stroke, stroke_weight=sw)

    # --- Transform helpers (minimal record-only implementations used in headless tests)
    def translate(self, x, y, z=None):
        """Translate the current matrix by x,y (,z).

        Records a 'translate' op to the engine graphics buffer so headless
        tests can assert transform usage.
        """
        # Delegate to engine so transform state is maintained
        try:
            return self._engine.translate(x, y, z)
        except Exception:
            try:
                args = {'x': float(x), 'y': float(y)}
                if z is not None:
                    args['z'] = float(z)
                return self._engine.graphics.record('translate', **args)
            except Exception:
                return None

    def rotate(self, angle):
        try:
            return self._engine.rotate(angle)
        except Exception:
            try:
                return self._engine.graphics.record('rotate', angle=float(angle))
            except Exception:
                return None

    def scale(self, sx, sy=None, sz=None):
        try:
            return self._engine.scale(sx, sy, sz)
        except Exception:
            try:
                if sy is None and sz is None:
                    return self._engine.graphics.record('scale', sx=float(sx))
                args = {'sx': float(sx), 'sy': float(sy) if sy is not None else float(sx)}
                if sz is not None:
                    args['sz'] = float(sz)
                return self._engine.graphics.record('scale', **args)
            except Exception:
                return None

    def push_matrix(self):
        try:
            return self._engine.push_matrix()
        except Exception:
            try:
                return self._engine.graphics.record('push_matrix')
            except Exception:
                return None

    def pop_matrix(self):
        try:
            return self._engine.pop_matrix()
        except Exception:
            try:
                return self._engine.graphics.record('pop_matrix')
            except Exception:
                return None

    def shear_x(self, angle):
        try:
            return self._engine.shear_x(angle)
        except Exception:
            try:
                return self._engine.graphics.record('shear_x', angle=float(angle))
            except Exception:
                return None

    def shear_y(self, angle):
        try:
            return self._engine.shear_y(angle)
        except Exception:
            try:
                return self._engine.graphics.record('shear_y', angle=float(angle))
            except Exception:
                return None

    def reset_matrix(self):
        try:
            return self._engine.reset_matrix()
        except Exception:
            try:
                return self._engine.graphics.record('reset_matrix')
            except Exception:
                return None

    def apply_matrix(self, *args):
        """Apply a matrix. Accepts either a single source matrix or 16 numbers."""
        try:
            return self._engine.apply_matrix(*args)
        except Exception:
            try:
                if len(args) == 1:
                    src = args[0]
                    return self._engine.graphics.record('apply_matrix', matrix=src)
                return self._engine.graphics.record('apply_matrix', values=list(args))
            except Exception:
                return None
