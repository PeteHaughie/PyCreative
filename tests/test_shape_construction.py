import os
import pygame
from pycreative.graphics import Surface, OffscreenSurface


def test_begin_vertex_end_triangle():
    # Create a small offscreen surface
    pygame.init()
    surf = pygame.Surface((100, 100))
    off = OffscreenSurface(surf)

    # Draw a filled triangle via begin/vertex/end
    off.begin_shape()
    off.vertex(10, 10)
    off.vertex(90, 10)
    off.vertex(50, 80)
    off.end_shape(close=True)

    # Sample a point roughly near the triangle centroid
    px = surf.get_at((50, 30))[:3]
    assert px != (0, 0, 0), f"Expected filled pixel, got {px}"

    pygame.quit()
