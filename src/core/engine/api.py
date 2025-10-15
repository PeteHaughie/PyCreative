from typing import TYPE_CHECKING, Any
from core.color import hsb_to_rgb

if TYPE_CHECKING:
    from .impl import Engine  # type: ignore


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
            self.pcvector = PCVector
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

    # lifecycle and environment helpers exposed to sketches
    def size(self, w: int, h: int):
        """Set sketch size (should be called in setup())."""
        self._engine._set_size(w, h)

    def window_title(self, title: str):
        """Set window title (if applicable)."""
        try:
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
        """Set background color. Accepts single grayscale, RGB (3) or HSB depending on color_mode.

        In 'RGB' mode inputs are treated as 0-255 RGB. In 'HSB' mode inputs are
        treated as H,S,B either 0-1 or 0-255 and converted to RGB.
        """
        mode = getattr(self._engine, 'color_mode', 'RGB')

        if len(args) == 1:
            v = args[0]
            if isinstance(v, (tuple, list)) and len(v) == 3:
                vals = v
            else:
                vals = (int(v), int(v), int(v))
        elif len(args) == 3:
            vals = args
        else:
            raise TypeError('background() expects 1 or 3 arguments')

        if str(mode).upper() == 'HSB':
            r, g, b = hsb_to_rgb(*vals)
        else:
            r, g, b = (int(vals[0]), int(vals[1]), int(vals[2]))

        # update engine background color and record op
        self._engine.background_color = (int(r), int(g), int(b))
        self._engine.graphics.record('background', r=int(r), g=int(g), b=int(b))
        # If a window exists (windowed mode), update the GL clear color
        try:
            win = getattr(self._engine, '_window', None)
            if win is not None:
                # lazy-import pyglet.gl to avoid import-time dependency
                from pyglet import gl
                gl.glClearColor(int(r) / 255.0, int(g) / 255.0, int(b) / 255.0, 1.0)
        except Exception:
            # Non-fatal: if pyglet isn't available or call fails, continue
            pass

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

    # new drawing state helpers
    def fill(self, *args):
        """Set fill color respecting color_mode (RGB or HSB)."""
        mode = getattr(self._engine, 'color_mode', 'RGB')
        if len(args) == 1:
            v = args[0]
            if isinstance(v, (tuple, list)) and len(v) == 3:
                vals = v
            else:
                vals = (int(v), int(v), int(v))
        elif len(args) == 3:
            vals = args
        else:
            raise TypeError('fill() expects 1 or 3 args')

        if str(mode).upper() == 'HSB':
            self._engine.fill_color = hsb_to_rgb(*vals)
        else:
            self._engine.fill_color = (int(vals[0]), int(vals[1]), int(vals[2]))

    def stroke(self, *args):
        """Set stroke color respecting color_mode (RGB or HSB)."""
        mode = getattr(self._engine, 'color_mode', 'RGB')
        if len(args) == 1:
            v = args[0]
            if isinstance(v, (tuple, list)) and len(v) == 3:
                vals = v
            else:
                vals = (int(v), int(v), int(v))
        elif len(args) == 3:
            vals = args
        else:
            raise TypeError('stroke() expects 1 or 3 args')

        if str(mode).upper() == 'HSB':
            self._engine.stroke_color = hsb_to_rgb(*vals)
        else:
            self._engine.stroke_color = (int(vals[0]), int(vals[1]), int(vals[2]))

    def stroke_weight(self, w: int):
        self._engine.stroke_weight = int(w)

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
