import pygame
from pycreative.graphics import Surface
from pycreative.vector import PVector


def test_pvector_works_with_surface():
    pygame.init()
    try:
        raw = pygame.Surface((50, 50), flags=pygame.SRCALPHA)
        s = Surface(raw)
        p = PVector(10, 12)
        # PVector should be iterable/unpackable and coercible by surface methods
        s.point(*p)
        s.ellipse(*p, 6, 6)
        s.circle(*p, 8)
        # polygon_with_style should accept list of tuples or PVectors (iterable)
        poly = [PVector(1, 1), PVector(5, 1), PVector(3, 4)]
        s.polygon_with_style([tuple(pt) for pt in poly], fill=(10, 10, 10))
    finally:
        pygame.quit()
