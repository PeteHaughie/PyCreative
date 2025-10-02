import pygame
from pycreative.graphics import OffscreenSurface


def test_hsb_fill_on_offscreen_quad():
    pygame.init()
    try:
        raw = pygame.Surface((120, 80), flags=pygame.SRCALPHA)
        off = OffscreenSurface(raw)

        # Set HSB mode and fill using HSB tuple; Color.from_hsb will convert
        off.color_mode('HSB', 360, 100, 100)
        # pick an HSB value with noticeable brightness
        off.fill((200, 80, 90))

        off.begin_shape('QUADS')
        off.vertex(10, 10)
        off.vertex(110, 10)
        off.vertex(110, 70)
        off.vertex(10, 70)
        off.end_shape()

        px = raw.get_at((60, 40))[:3]
        # pixel should not be black if fill applied
        assert px != (0, 0, 0)
    finally:
        pygame.quit()
