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
        segments: int = 100,
    ):
        """
        Draw an arc centered at (x, y) with width w and height h from start_angle to end_angle.
        Angles are in radians.
        mode: 'open' (default), 'chord', or 'pie'.
        - 'open': just the arc
        - 'chord': arc plus line between endpoints, can be filled
        - 'pie': arc plus lines from endpoints to center, can be filled
        """
        import math
        cx, cy = x, y
        rx, ry = w / 2, h / 2
        # Generate arc points
        arc_points = [
            (
                cx + rx * math.cos(start_angle + (end_angle - start_angle) * i / segments),
                cy + ry * math.sin(start_angle + (end_angle - start_angle) * i / segments),
            )
            for i in range(segments + 1)
        ]
        # Draw outline
        if mode == "open":
            pygame.draw.lines(self.surface, color, False, arc_points, width)
        elif mode == "chord":
            pygame.draw.lines(self.surface, color, False, arc_points, width)
            pygame.draw.line(self.surface, color, arc_points[0], arc_points[-1], width)
        elif mode == "pie":
            pygame.draw.lines(self.surface, color, False, arc_points, width)
            pygame.draw.line(self.surface, color, (cx, cy), arc_points[0], width)
            pygame.draw.line(self.surface, color, (cx, cy), arc_points[-1], width)
        # Draw fill (polygon)
        if width == 0:
            if mode == "chord":
                poly = arc_points + [arc_points[-1], arc_points[0]]
                pygame.draw.polygon(self.surface, color, poly, 0)
            elif mode == "pie":
                poly = [ (cx, cy) ] + arc_points
                pygame.draw.polygon(self.surface, color, poly, 0)
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
