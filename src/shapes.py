"""
Module for drawing basic geometric shapes using Pygame.
"""
import pygame

class ShapeDrawer:
    """
    Draws basic geometric shapes on a Pygame surface.
    """
    def __init__(self, surface):
        """
        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        self.surface = surface

    def draw_rectangle(self, rect, color, width=0):
        """
        Draw a rectangle.
        Args:
            rect (tuple): (x, y, w, h)
            color (tuple): (R, G, B)
            width (int): Border width. 0 = filled.
        """
        pygame.draw.rect(self.surface, color, rect, width)

    def draw_circle(self, center, radius, color, width=0):
        """
        Draw a circle.
        Args:
            center (tuple): (x, y)
            radius (int): Radius
            color (tuple): (R, G, B)
            width (int): Border width. 0 = filled.
        """
        pygame.draw.circle(self.surface, color, center, radius, width)

    def draw_line(self, start_pos, end_pos, color, width=1):
        """
        Draw a line.
        Args:
            start_pos (tuple): (x1, y1)
            end_pos (tuple): (x2, y2)
            color (tuple): (R, G, B)
            width (int): Line width.
        """
        pygame.draw.line(self.surface, color, start_pos, end_pos, width)
