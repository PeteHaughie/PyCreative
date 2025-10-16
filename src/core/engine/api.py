from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from .impl import Engine


class SimpleSketchAPI:
    """Lightweight object passed to sketches as `this`.

    It offers convenience methods that delegate to the Engine's API registry
    and control lifecycle behaviour (size/no_loop/loop/redraw/save_frame).
    """

    def __init__(self, engine: 'Engine'):
        self._engine = engine
        # expose PCVector constructor to sketches as `this.pcvector`
        try:
            from core.math import PCVector  # local import to avoid top-level cost
            # provide a small factory so sketches can do `v = this.pcvector()`
            self.pcvector: Any = PCVector
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
