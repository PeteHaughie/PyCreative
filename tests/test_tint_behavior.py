import pygame

from pycreative.graphics import Surface


def test_tint_alpha_only_and_rgb():
    pygame.init()
    try:
        dst = Surface(pygame.Surface((6, 2), flags=pygame.SRCALPHA))
        # create white source so multiplication yields exact predictable values
        src = pygame.Surface((2, 2), flags=pygame.SRCALPHA)
        src.fill((255, 255, 255, 255))

        # no tint: draw at 0,0
        dst.image_mode(dst.MODE_CORNER)
        dst.tint(None)
        dst.image(src, 0, 0)
        p = dst.raw.get_at((0, 0))
        assert p[:3] == (255, 255, 255)

        # alpha only tint: tint(255, 126) should only change alpha
        dst = Surface(pygame.Surface((6, 2), flags=pygame.SRCALPHA))
        dst.image_mode(dst.MODE_CORNER)
        dst.tint(255, 126)
        dst.image(src, 0, 0)
        p = dst.raw.get_at((0, 0))
        # multiplication by 255 keeps color as-is; alpha should be reduced
        assert p[:3] == (255, 255, 255)
        assert p[3] <= 126

        # rgb tint with alpha: tint(0,153,204,126) on white should yield roughly (0,153,204) with alpha <=126
        dst = Surface(pygame.Surface((6, 2), flags=pygame.SRCALPHA))
        dst.tint(0, 153, 204, 126)
        dst.image(src, 0, 0)
        p = dst.raw.get_at((0, 0))
        assert p[0] == 0
        assert p[1] == 153
        assert p[2] == 204
        assert p[3] <= 126
    finally:
        pygame.quit()
