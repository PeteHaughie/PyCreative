"""
pycreative.graphics: Surface wrapper with drawing helpers.
TODO: Add CENTERMODE and stroke caps/join options
"""

try:
    import cairocffi as cairo
except ImportError:
    cairo = None

from typing import Self
from abc import ABC, abstractmethod
import pygame
import numpy as np
import io


class SurfaceBase(ABC):
    @abstractmethod
    def rect(self, x, y, w, h, color=(255, 255, 255), width=0) -> Self:
        pass

    @abstractmethod
    def ellipse(self, x, y, w, h, color=(255, 255, 255), width=0) -> Self:
        pass

    @abstractmethod
    def line(self, x1, y1, x2, y2, color=(255, 255, 255), width=1) -> Self:
        pass

    @abstractmethod
    def triangle(self, x1, y1, x2, y2, x3, y3, color=(255, 255, 255), width=0) -> Self:
        pass

    @abstractmethod
    def quad(
        self, x1, y1, x2, y2, x3, y3, x4, y4, color=(255, 255, 255), width=0
    ) -> Self:
        pass

    @abstractmethod
    def arc(
        self,
        x,
        y,
        w,
        h,
        start_angle,
        end_angle,
        color=(255, 255, 255),
        width=1,
        mode="open",
        segments=100,
    ) -> Self:
        pass

    @abstractmethod
    def bezier(
        self,
        x1,
        y1,
        x2,
        y2,
        x3,
        y3,
        x4,
        y4,
        color=(255, 255, 255),
        width=1,
        segments=100,
    ) -> Self:
        pass

    @abstractmethod
    def image(self, img, x, y, w=None, h=None) -> Self:
        pass


class CairoSurface(SurfaceBase):
    def _normalize_color(self, color):
        # Accept int or tuple/list for RGB
        if isinstance(color, int):
            color = (color, color, color)
        elif isinstance(color, (list, tuple)) and len(color) == 1:
            color = (color[0], color[0], color[0])
        return [c / 255.0 for c in color[:3]]

    def clear(self, color=(255, 0, 255)):
        r, g, b = self._normalize_color(color)
        self.ctx.save()
        self.ctx.set_source_rgb(r, g, b)
        if cairo and hasattr(cairo, "OPERATOR_SOURCE"):
            self.ctx.set_operator(cairo.OPERATOR_SOURCE)
        self.ctx.rectangle(0, 0, self.width, self.height)
        self.ctx.fill()
        self.ctx.restore()

    def __init__(self, width: int, height: int):
        if cairo is None:
            raise ImportError("cairocffi is required for CairoSurface")
        self.width = width
        self.height = height
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self.surface)

    def line(self, x1, y1, x2, y2, color=(255, 255, 255), width=1) -> Self:
        r, g, b = self._normalize_color(color)
        self.ctx.set_source_rgb(r, g, b)
        self.ctx.set_line_width(width)
        self.ctx.move_to(x1, y1)
        self.ctx.line_to(x2, y2)
        self.ctx.stroke()
        return self

    def rect(self, x, y, w, h, color=(255, 255, 255), width=0) -> Self:
        r, g, b = self._normalize_color(color)
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
        return self

    def ellipse(self, x, y, w, h, color=(255, 255, 255), width=0) -> Self:
        r, g, b = self._normalize_color(color)
        self.ctx.save()
        self.ctx.translate(x, y)
        self.ctx.scale(w / 2, h / 2)
        self.ctx.arc(0, 0, 1, 0, 2 * np.pi)
        if width == 0:
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.fill()
        else:
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.set_line_width(width / ((w + h) / 2) * 2)
            self.ctx.stroke()
        self.ctx.restore()
        return self

    def triangle(self, x1, y1, x2, y2, x3, y3, color=(255, 255, 255), width=0) -> Self:
        r, g, b = self._normalize_color(color)
        self.ctx.save()
        self.ctx.move_to(x1, y1)
        self.ctx.line_to(x2, y2)
        self.ctx.line_to(x3, y3)
        self.ctx.close_path()
        if width == 0:
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.fill()
        else:
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.set_line_width(width)
            self.ctx.stroke()
        self.ctx.restore()
        return self

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4, color=(255, 255, 255), width=0) -> Self:
        r, g, b = self._normalize_color(color)
        self.ctx.save()
        self.ctx.move_to(x1, y1)
        self.ctx.line_to(x2, y2)
        self.ctx.line_to(x3, y3)
        self.ctx.line_to(x4, y4)
        self.ctx.close_path()
        if width == 0:
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.fill()
        else:
            self.ctx.set_source_rgb(r, g, b)
            self.ctx.set_line_width(width)
            self.ctx.stroke()
        self.ctx.restore()
        return self

    def arc(
        self,
        x,
        y,
        w,
        h,
        start_angle,
        end_angle,
        color=(255, 255, 255),
        width=1,
        mode="open",
        segments=100,
    ) -> Self:
        r, g, b = self._normalize_color(color)
        self.ctx.save()
        self.ctx.translate(x, y)
        self.ctx.scale(w / 2, h / 2)
        self.ctx.set_line_width(width / ((w + h) / 2) * 2)
        self.ctx.set_source_rgb(r, g, b)
        self.ctx.arc(0, 0, 1, start_angle, end_angle)
        if mode == "open":
            self.ctx.stroke()
        elif mode == "chord":
            if width == 0:
                self.ctx.line_to(np.cos(end_angle), np.sin(end_angle))
                self.ctx.line_to(np.cos(start_angle), np.sin(start_angle))
                self.ctx.close_path()
                self.ctx.set_source_rgb(r, g, b)
                self.ctx.fill()
            else:
                self.ctx.stroke()
                self.ctx.move_to(np.cos(start_angle), np.sin(start_angle))
                self.ctx.line_to(np.cos(end_angle), np.sin(end_angle))
                self.ctx.stroke()
        elif mode == "pie":
            if width == 0:
                self.ctx.line_to(0, 0)
                self.ctx.close_path()
                self.ctx.set_source_rgb(r, g, b)
                self.ctx.fill()
            else:
                self.ctx.stroke()
        self.ctx.restore()
        return self

    def bezier(
        self,
        x1,
        y1,
        x2,
        y2,
        x3,
        y3,
        x4,
        y4,
        color=(255, 255, 255),
        width=1,
        segments=100,
    ) -> Self:
        r, g, b = self._normalize_color(color)
        self.ctx.save()
        self.ctx.set_source_rgb(r, g, b)
        self.ctx.set_line_width(width)
        self.ctx.move_to(x1, y1)
        self.ctx.curve_to(x2, y2, x3, y3, x4, y4)
        self.ctx.stroke()
        self.ctx.restore()
        return self

    def image(self, img, x, y, w=None, h=None) -> Self:
        """
        Draw an image onto the CairoSurface. Accepts PIL.Image or PyGame Surface.
        """
        buf = io.BytesIO()
        # Accept PIL.Image or PyGame Surface
        from PIL import Image
        import pygame

        if hasattr(img, "save") and callable(img.save):
            pil_img = img
        elif hasattr(img, "get_buffer") or hasattr(img, "get_view"):
            # Convert PyGame Surface to PIL.Image
            arr = pygame.surfarray.array3d(img)
            arr = arr.swapaxes(0, 1)
            pil_img = Image.fromarray(arr)
        else:
            raise TypeError(
                "CairoSurface.image only supports PIL.Image or PyGame Surface input"
            )
        pil_img.save(buf, format="PNG")
        buf.seek(0)
        img_surface = cairo.ImageSurface.create_from_png(buf)
        self.ctx.save()
        if w is not None and h is not None:
            self.ctx.translate(x, y)
            self.ctx.scale(w / img_surface.get_width(), h / img_surface.get_height())
            self.ctx.set_source_surface(img_surface, 0, 0)
        else:
            self.ctx.set_source_surface(img_surface, x, y)
        self.ctx.paint()
        self.ctx.restore()
        return self

    def to_pygame_surface(self):
        import pygame
        import numpy as np

        self.surface.flush()  # Ensure Cairo writes all pixels
        buf = bytes(self.surface.get_data()[:])
        arr = np.frombuffer(buf, dtype=np.uint8).reshape((self.height, self.width, 4))
        arr = np.transpose(arr, (1, 0, 2))  # Swap axes to (height, width, 4)
        # Convert ARGB32 (Cairo) to RGB for PyGame
        rgb = arr[:, :, [2, 1, 0]]  # BGRA -> RGB
        surface = pygame.surfarray.make_surface(rgb)
        return surface

    def debug_draw(self):
        # Draw a filled red rectangle and a thick green line
        self.ctx.save()
        self.ctx.set_source_rgb(1, 0, 0)
        self.ctx.rectangle(10, 10, 100, 100)
        self.ctx.fill()
        self.ctx.set_source_rgb(0, 1, 0)
        self.ctx.set_line_width(10)
        self.ctx.move_to(10, 150)
        self.ctx.line_to(200, 150)
        self.ctx.stroke()
        self.ctx.restore()


class Surface(SurfaceBase):
    def __init__(self, surface: pygame.Surface):
        self.surface = surface

    def rect(self, x, y, w, h, color=(255, 255, 255), width=0) -> Self:
        pygame.draw.rect(self.surface, color, (x, y, w, h), width)
        return self

    def ellipse(self, x, y, w, h, color=(255, 255, 255), width=0) -> Self:
        pygame.draw.ellipse(self.surface, color, (x - w / 2, y - h / 2, w, h), width)
        return self

    def line(self, x1, y1, x2, y2, color=(255, 255, 255), width=1) -> Self:
        pygame.draw.line(self.surface, color, (x1, y1), (x2, y2), width)
        return self

    def triangle(self, x1, y1, x2, y2, x3, y3, color=(255, 255, 255), width=0) -> Self:
        pygame.draw.polygon(self.surface, color, [(x1, y1), (x2, y2), (x3, y3)], width)
        return self

    def quad(
        self, x1, y1, x2, y2, x3, y3, x4, y4, color=(255, 255, 255), width=0
    ) -> Self:
        pygame.draw.polygon(
            self.surface, color, [(x1, y1), (x2, y2), (x3, y3), (x4, y4)], width
        )
        return self

    def arc(
        self,
        x,
        y,
        w,
        h,
        start_angle,
        end_angle,
        color=(255, 255, 255),
        width=1,
        mode="open",
        segments=100,
    ) -> Self:
        import math

        cx, cy = x, y
        rx, ry = w / 2, h / 2
        arc_points = [
            (
                cx
                + rx * math.cos(start_angle + (end_angle - start_angle) * i / segments),
                cy
                + ry * math.sin(start_angle + (end_angle - start_angle) * i / segments),
            )
            for i in range(segments + 1)
        ]
        if mode == "open":
            pygame.draw.lines(self.surface, color, False, arc_points, width)
        elif mode == "chord":
            pygame.draw.lines(self.surface, color, False, arc_points, width)
            pygame.draw.line(self.surface, color, arc_points[0], arc_points[-1], width)
        elif mode == "pie":
            pygame.draw.lines(self.surface, color, False, arc_points, width)
            pygame.draw.line(self.surface, color, (cx, cy), arc_points[0], width)
            pygame.draw.line(self.surface, color, (cx, cy), arc_points[-1], width)
        if width == 0:
            if mode == "chord":
                poly = arc_points + [arc_points[-1], arc_points[0]]
                pygame.draw.polygon(self.surface, color, poly, 0)
            elif mode == "pie":
                poly = [(cx, cy)] + arc_points
                pygame.draw.polygon(self.surface, color, poly, 0)
        return self

    def bezier(
        self,
        x1,
        y1,
        x2,
        y2,
        x3,
        y3,
        x4,
        y4,
        color=(255, 255, 255),
        width=1,
        segments=100,
    ) -> Self:
        def cubic_bezier(t):
            x = (
                (1 - t) ** 3 * x1
                + 3 * (1 - t) ** 2 * t * x2
                + 3 * (1 - t) * t**2 * x3
                + t**3 * x4
            )
            y = (
                (1 - t) ** 3 * y1
                + 3 * (1 - t) ** 2 * t * y2
                + 3 * (1 - t) * t**2 * y3
                + t**3 * y4
            )
            return (x, y)

        curve_points = [cubic_bezier(s / segments) for s in range(segments + 1)]
        pygame.draw.lines(self.surface, color, False, curve_points, width)
        return self

    def image(self, img, x, y, w=None, h=None) -> Self:
        if w is not None and h is not None:
            img = pygame.transform.scale(img, (int(w), int(h)))
        self.surface.blit(img, (x, y))
        return self
