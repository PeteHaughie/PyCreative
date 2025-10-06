import pygame

from pycreative.graphics import Surface


def test_tint_alpha_clamps_and_applies():
    pygame.init()
    try:
        # setup destination wrapper
        dst = Surface(pygame.Surface((4, 4), flags=pygame.SRCALPHA))
        dst.image_mode(dst.MODE_CORNER)

        # white source fully opaque
        src = pygame.Surface((1, 1), flags=pygame.SRCALPHA)
        src.fill((255, 255, 255, 255))

        # negative alpha -> clamp to 0
        dst.tint(255, -5)
        assert dst.tint()[3] == 0
        dst.image(src, 0, 0)
        p = dst.raw.get_at((0, 0))
        assert p[3] == 0

        # zero alpha -> fully transparent
        dst = Surface(pygame.Surface((4, 4), flags=pygame.SRCALPHA))
        dst.image_mode(dst.MODE_CORNER)
        dst.tint(255, 0)
        assert dst.tint()[3] == 0
        dst.image(src, 0, 0)
        p = dst.raw.get_at((0, 0))
        assert p[3] == 0

        # mid alpha
        dst = Surface(pygame.Surface((4, 4), flags=pygame.SRCALPHA))
        dst.image_mode(dst.MODE_CORNER)
        dst.tint(255, 123)
        assert dst.tint()[3] == 123
        dst.image(src, 0, 0)
        p = dst.raw.get_at((0, 0))
        assert p[3] <= 123

        # large alpha >255 -> clamp to 255
        dst = Surface(pygame.Surface((4, 4), flags=pygame.SRCALPHA))
        dst.image_mode(dst.MODE_CORNER)
        dst.tint(255, 999)
        assert dst.tint()[3] == 255
        dst.image(src, 0, 0)
        p = dst.raw.get_at((0, 0))
        assert p[3] == 255
    finally:
        pygame.quit()
