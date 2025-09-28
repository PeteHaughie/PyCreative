from pycreative.style import GraphicsStyle

class GraphicsSurface(GraphicsStyle):
    """
    Supports PyGame and Cairo backends.
    import cairocffi as cairo
    Args:
        width (int): Surface width
        height (int): Surface height
        mode (str): 'cairo'

    Attributes:
        surface: PyGame Surface or Cairo ImageSurface
        ctx: Cairo Context (if mode='cairo')
        width: int
        height: int
        mode: str

    Usage:
        g = GraphicsSurface(320, 240, mode='pygame')
        g.clear((0,0,0))
        g.line(0,0,100,100,color=(255,0,0),width=2)
        ...
        sketch.image(g.surface, x, y, w, h)
    """
    def __init__(self, width: int, height: int):
        super().__init__()
        self.width = width
        self.height = height
        self._cairo_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self._cairo_surface)
        self._pygame_surface = None
"""
pycreative.graphics: GraphicsSurface for in-memory drawing and manipulation (offscreen surface).

Offscreen graphics surface for in-memory drawing and manipulation.
Uses Cairo for all rendering and pixel operations.

Args:
    width (int): Surface width
    height (int): Surface height

Attributes:
    surface: PyGame Surface (converted from Cairo ImageSurface)
    ctx: Cairo Context
    width: int
    height: int

Usage:
    g = GraphicsSurface(320, 240)
    g.clear((0,0,0))
    g.line(0,0,100,100,color=(255,0,0),width=2)
    ...
    sketch.image(g.surface, x, y, w, h)
"""
import pygame
import numpy as np
try:
    import cairocffi as cairo
except ImportError:
    cairo = None
from typing import Optional

class GraphicsSurface:
    def translate(self, x: float, y: float):
        """
        Translate the origin by (x, y).
        Usage:
            surface.translate(100, 50)
        """
        self.ctx.translate(x, y)

    def rotate(self, angle: float):
        """
        Rotate the drawing context by angle (in radians).
        Usage:
            surface.rotate(math.pi / 4)
        """
        self.ctx.rotate(angle)

    def scale(self, sx: float, sy: float = 1.0):
        """
        Scale the drawing context by (sx, sy).
        Usage:
            surface.scale(2, 1)
        """
        self.ctx.scale(sx, sy)
    def push(self):
        """
        Save the current transformation matrix and drawing state.
        Usage:
            surface.push()
        """
        self.ctx.save()

    def pop(self):
        """
        Restore the previous transformation matrix and drawing state.
        Usage:
            surface.pop()
        """
        self.ctx.restore()
    def fill(self, *args):
        """
        Set fill color for subsequent shapes.
        Usage:
            surface.fill(255, 0, 0) or surface.fill((255,0,0))
        """
        if len(args) == 0:
            self._fill = None
        elif len(args) > 1:
            self._fill = args
        else:
            self._fill = args[0]
        self._do_fill = True
    def rect_mode(self, mode: str):
        """
        Set the rectangle drawing mode.
        Modes:
            'corner'  (default): x, y is top-left, w/h are width/height
            'center': x, y is center, w/h are width/height
            'corners': x, y and w, h are opposite corners
        Usage:
            surface.rect_mode('center')
        """
        if mode not in ("corner", "center", "corners"):
            raise ValueError(f"rect_mode must be 'corner', 'center', or 'corners', got '{mode}'")
        self._rect_mode = mode
    def noStroke(self):
        """
        Disable stroke for subsequent shapes.
        Usage:
            surface.noStroke()
        """
        if hasattr(self, '_do_stroke'):
            self._do_stroke = False
    def bg(self, color=(0,0,0)):
        """
        Set the background color of the surface. Equivalent to clear(color).
        Usage:
            surface.bg((255,255,255))
        """
        self.clear(color)
    """
import numpy as np
    Supports PyGame and Cairo backends.
    import cairocffi as cairo
    Args:
        width (int): Surface width
        height (int): Surface height
        mode (str): 'cairo'

    Attributes:
        surface: PyGame Surface or Cairo ImageSurface
        ctx: Cairo Context (if mode='cairo')
        width: int
        height: int
        mode: str

    Usage:
        g = GraphicsSurface(320, 240, mode='pygame')
        g.clear((0,0,0))
        g.line(0,0,100,100,color=(255,0,0),width=2)
        ...
        sketch.image(g.surface, x, y, w, h)
    """
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self._cairo_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self._cairo_surface)
        self._pygame_surface = None

    @property
    def surface(self):
        """
        Returns a PyGame Surface for display, converting from Cairo if needed.
        """
        buf = self._cairo_surface.get_data()
        arr = np.ndarray(shape=(self.height, self.width, 4), dtype=np.uint8, buffer=buf)
        rgba = arr[..., [2,1,0,3]]  # ARGB to RGBA
        surf = pygame.image.frombuffer(rgba.tobytes(), (self.width, self.height), 'RGBA')
        return surf

    def clear(self, color=(0,0,0)):
        r, g, b = [c/255.0 for c in color[:3]]
        self.ctx.save()
        self.ctx.set_source_rgb(r, g, b)
        self.ctx.set_operator(cairo.OPERATOR_SOURCE)
        self.ctx.rectangle(0, 0, self.width, self.height)
        self.ctx.fill()
        self.ctx.restore()

    def line(self, x1, y1, x2, y2, color=(255,255,255), width=1):
        r, g, b = [c/255.0 for c in color[:3]]
        self.ctx.save()
        self.ctx.set_source_rgb(r, g, b)
        self.ctx.set_line_width(width)
        self.ctx.move_to(x1, y1)
        self.ctx.line_to(x2, y2)
        self.ctx.stroke()
        self.ctx.restore()

    def rect(self, x, y, w, h, color=(255,255,255), width=0):
        r, g, b = [c/255.0 for c in color[:3]]
        self.ctx.save()
        self.ctx.rectangle(x, y, w, h)
        if width == 0:
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.fill()
        else:
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.set_line_width(width)
            self.ctx.stroke()
        self.ctx.restore()

    def ellipse(self, x, y, w, h, color=(255,255,255), width=0):
        r, g, b = [c/255.0 for c in color[:3]]
        self.ctx.save()
        self.ctx.translate(x + w/2, y + h/2)
        self.ctx.scale(w/2, h/2)
        self.ctx.arc(0, 0, 1, 0, 2*3.14159)
        if width == 0:
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.fill()
        else:
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.set_line_width(width)
            self.ctx.stroke()
        self.ctx.restore()

    def get_pixels(self) -> Optional[np.ndarray]:
        buf = self.surface.get_data()
        arr = np.ndarray(shape=(self.height, self.width, 4), dtype=np.uint8, buffer=buf)
        return arr

    def set_pixels(self, arr: np.ndarray):
        buf = self.surface.get_data()
        np.copyto(np.ndarray(shape=(self.height, self.width, 4), dtype=np.uint8, buffer=buf), arr)

    def image(self, img, x, y, w=None, h=None):
        # Only supports PNG via Cairo
        import io
        if hasattr(img, 'save'):
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            img_surface = cairo.ImageSurface.create_from_png(buf)
            self.ctx.save()
            self.ctx.set_source_surface(img_surface, x, y)
            self.ctx.paint()
            self.ctx.restore()

    def to_pygame_surface(self):
        """
        Convert the Cairo ImageSurface to a PyGame Surface for display.
        Returns a pygame.Surface.
        """
        buf = self.surface.get_data()
        arr = np.ndarray(shape=(self.height, self.width, 4), dtype=np.uint8, buffer=buf)
        # Convert ARGB to RGBA for PyGame
        rgba = arr[..., [2,1,0,3]]  # BGR -> RGB, alpha stays
        surf = pygame.image.frombuffer(rgba.tobytes(), (self.width, self.height), 'RGBA')
        return surf
