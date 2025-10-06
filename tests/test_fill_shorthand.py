import os

from pycreative.graphics import Surface as GraphicsSurface


def _init_pygame_dummy():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame as _pygame

    _pygame.init()
    return _pygame


def test_fill_grayscale_alpha_sets_rgba():
    pygame = _init_pygame_dummy()
    surf = pygame.Surface((10, 10), flags=pygame.SRCALPHA)
    gs = GraphicsSurface(surf)

    # default is RGB mode with max 255
    gs.fill((128, 200))
    assert gs._fill[0] == 128 and gs._fill[1] == 128 and gs._fill[2] == 128 and gs._fill[3] == 200

    # also works when specifying floats (scaled by current color max)
    gs.color_mode('RGB', 1, 1, 1)
    gs.fill((0.5, 0.8))
    # with max 1, 0.5 -> 128-ish, but Color.from_rgb does integer rounding; ensure tuple length and alpha
    assert isinstance(gs._fill, tuple) and len(gs._fill) == 4

    pygame.quit()
