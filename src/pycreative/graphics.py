from typing import Any, Optional
import pygame

class Surface:
    """
    Wrapper for pygame.Surface with drawing helpers.

    Usage example:
        surf = Surface(pygame.Surface((640, 480)))
        surf.rect(10, 10, 100, 50, color=(255,0,0))
        surf.ellipse(320, 240, 200, 100, color=(0,255,0))
        surf.line((0,0), (640,480), color=(0,0,255), width=3)
        surf.image(pygame.image.load("example.png"), 50, 50)
    """

    def __init__(self, surface: pygame.Surface):
        self.surface = surface

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        color: Any = (255, 255, 255),
        width: int = 0,
    ):
        """
        Draw a rectangle at (x, y) with width w and height h.
        Parameters:
        - x, y: Top-left corner
        - w, h: Width and height
        - color: RGB tuple
        - width: Border thickness (0 = filled)
        """
        pygame.draw.rect(self.surface, color, (x, y, w, h), width)
        return self

    def ellipse(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        color: Any = (255, 255, 255),
        width: int = 0,
    ):
        """
        Draw an ellipse centered at (x, y) with width w and height h.
        Parameters:
        - x, y: Center coordinates
        - w, h: Width and height
        - color: RGB tuple
        - width: Border thickness (0 = filled)
        """
        pygame.draw.ellipse(self.surface, color, (x - w / 2, y - h / 2, w, h), width)
        return self

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: Any = (255, 255, 255),
        width: int = 1,
    ):
        """
        Draw a line from (x1, y1) to (x2, y2).
        Parameters:
        - x1, y1: Start coordinates
        - x2, y2: End coordinates
        - color: RGB tuple
        - width: Line thickness
        """
        pygame.draw.line(self.surface, color, (x1, y1), (x2, y2), width)
        return self

    def triangle(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        color: Any = (255, 255, 255),
        width: int = 0,
    ):
        pygame.draw.polygon(self.surface, color, [(x1, y1), (x2, y2), (x3, y3)], width)
        return self
    
    def quad(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        x4: float,
        y4: float,
        color: Any = (255, 255, 255),
        width: int = 0,
    ):
        pygame.draw.polygon(self.surface, color, [(x1, y1), (x2, y2), (x3, y3), (x4, y4)], width)
        return self

    def arc(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        start_angle: float,
        end_angle: float,
        color: Any = (255, 255, 255),
        width: int = 1,
        mode: str = "open",
    ):
        """
        Draw an arc centered at (x, y) with width w and height h from start_angle to end_angle.
        Angles are in radians.
        mode: 'open' (default), 'chord', or 'pie'.
        - 'open': just the arc
        - 'chord': arc plus line between endpoints
        - 'pie': arc plus lines from endpoints to center
        """
        rect = (x - w / 2, y - h / 2, w, h)
        # Draw the arc itself
        pygame.draw.arc(self.surface, color, rect, start_angle, end_angle, width)
        # Calculate endpoints
        import math
        cx, cy = x, y
        rx, ry = w / 2, h / 2
        x0 = cx + rx * math.cos(start_angle)
        y0 = cy + ry * math.sin(start_angle)
        x1 = cx + rx * math.cos(end_angle)
        y1 = cy + ry * math.sin(end_angle)
        if mode == "chord":
            pygame.draw.line(self.surface, color, (x0, y0), (x1, y1), width)
        elif mode == "pie":
            pygame.draw.line(self.surface, color, (cx, cy), (x0, y0), width)
            pygame.draw.line(self.surface, color, (cx, cy), (x1, y1), width)
        return self

    def bezier(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        x3: float,
        y3: float,
        x4: float,
        y4: float,
        color: Any = (255, 255, 255),
        width: int = 1,
        segments: int = 100,
    ):
        """
        Draw a cubic Bezier curve from (x1, y1) to (x4, y4) with control points (x2, y2), (x3, y3).
        - color: RGB tuple
        - width: Line thickness
        - segments: Number of line segments to approximate the curve
        """
        def cubic_bezier(t):
            x = (
                (1 - t) ** 3 * x1
                + 3 * (1 - t) ** 2 * t * x2
                + 3 * (1 - t) * t ** 2 * x3
                + t ** 3 * x4
            )
            y = (
                (1 - t) ** 3 * y1
                + 3 * (1 - t) ** 2 * t * y2
                + 3 * (1 - t) * t ** 2 * y3
                + t ** 3 * y4
            )
            return (x, y)
        curve_points = [cubic_bezier(s / segments) for s in range(segments + 1)]
        pygame.draw.lines(self.surface, color, False, curve_points, width)
        return self

    def image(
        self,
        img: pygame.Surface,
        x: float,
        y: float,
        w: Optional[float] = None,
        h: Optional[float] = None,
    ):
        """
        Draw an image at (x, y). If w and h are provided, scale the image to that size.
        """
        if w is not None and h is not None:
            img = pygame.transform.scale(img, (int(w), int(h)))
        self.surface.blit(img, (x, y))
        return self
