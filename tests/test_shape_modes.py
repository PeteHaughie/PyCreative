import pygame
from pycreative.graphics import OffscreenSurface


def _make_surface(w=120, h=80):
    pygame.init()
    surf = pygame.Surface((w, h))
    off = OffscreenSurface(surf)
    return pygame, surf, off


def test_points_mode_draws_pixels():
    pygame, surf, off = _make_surface()
    try:
        off.stroke((255, 0, 0))
        off.stroke_weight(4)
        off.begin_shape('POINTS')
        off.vertex(10, 10)
        off.vertex(20, 20)
        off.vertex(30, 10)
        off.end_shape()

        # At least one of the specified points should have a non-black pixel
        px = surf.get_at((10, 10))[:3]
        assert px != (0, 0, 0)
    finally:
        pygame.quit()


def test_lines_mode_draws_segment():
    pygame, surf, off = _make_surface()
    try:
        off.stroke((0, 255, 0))
        off.stroke_weight(3)
        off.begin_shape('LINES')
        off.vertex(5, 5)
        off.vertex(60, 5)
        off.vertex(5, 15)
        off.vertex(60, 15)
        off.end_shape()

        # sample a point along the first horizontal segment
        px = surf.get_at((30, 5))[:3]
        assert px != (0, 0, 0)
    finally:
        pygame.quit()


def test_triangles_and_quads_modes_fill():
    pygame, surf, off = _make_surface()
    try:
        off.fill((0, 0, 255))
        off.begin_shape('TRIANGLES')
        off.vertex(10, 40)
        off.vertex(60, 10)
        off.vertex(110, 40)
        off.end_shape()

        # a point inside the triangle should be filled
        px = surf.get_at((60, 30))[:3]
        assert px != (0, 0, 0)

        # test quads: draw a filled quad and sample inside
        off.fill((255, 128, 0))
        off.begin_shape('QUADS')
        off.vertex(10, 50)
        off.vertex(50, 50)
        off.vertex(50, 70)
        off.vertex(10, 70)
        off.end_shape()

        px2 = surf.get_at((30, 60))[:3]
        assert px2 != (0, 0, 0)
    finally:
        pygame.quit()
