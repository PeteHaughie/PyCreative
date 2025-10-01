import pygame
from pycreative.app import Sketch
from pycreative.graphics import OffscreenSurface, Surface


def test_sketch_wrappers_draw_on_main_surface():
    pygame.init()
    try:
        raw = pygame.Surface((120, 80), flags=pygame.SRCALPHA)
        sk = Sketch()
        # Attach a Surface wrapper to the sketch so sketch wrappers delegate
        sk.surface = Surface(raw)

        # Use sketch-level begin_shape/vertex/end_shape wrappers
        sk.fill((10, 120, 200))
        sk.begin_shape('TRIANGLES')
        sk.vertex(10, 10)
        sk.vertex(60, 10)
        sk.vertex(35, 60)
        sk.end_shape()

        px = raw.get_at((35, 30))[:3]
        assert px != (0, 0, 0)
    finally:
        pygame.quit()


def test_create_graphics_offscreen_supports_modes():
    pygame.init()
    try:
        sk = Sketch()
        off = sk.create_graphics(140, 100)
        assert isinstance(off, OffscreenSurface)

        off.fill((200, 50, 50))
        off.begin_shape('QUADS')
        off.vertex(10, 10)
        off.vertex(120, 10)
        off.vertex(120, 80)
        off.vertex(10, 80)
        off.end_shape()

        # sample center pixel of offscreen surface
        raw = off._surf  # pygame.Surface
        px = raw.get_at((60, 45))[:3]
        assert px != (0, 0, 0)
    finally:
        pygame.quit()
