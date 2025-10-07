import pytest
import pygame
from pycreative.graphics import Surface


def _mk_surfaces():
    # create headless-friendly surfaces
    main = pygame.Surface((50, 50))
    src = pygame.Surface((10, 10), flags=pygame.SRCALPHA)
    return main, src


def _fill_background_and_source(surf: Surface, src_surf: pygame.Surface):
    # background: solid blue
    surf.clear((0, 0, 255))
    # source: solid red, fully opaque
    src_surf.fill((255, 0, 0, 255))


@pytest.mark.parametrize(
    "mode,expected",
    [
        (Surface.BLEND, (255, 0, 0)),
        (Surface.ADD, (255, 0, 255)),
        (Surface.SUBTRACT, (0, 0, 255)),
        (Surface.DARKEST, (0, 0, 0)),
        (Surface.LIGHTEST, (255, 0, 255)),
        (Surface.DIFFERENCE, (255, 0, 255)),
        (Surface.EXCLUSION, (255, 0, 255)),
        (Surface.MULTIPLY, (0, 0, 0)),
        (Surface.SCREEN, (255, 0, 255)),
        (Surface.REPLACE, (255, 0, 0)),
    ],
)
def test_blend_mode_results(monkeypatch, mode, expected):
    # run headless
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    pygame.init()

    main_surf, src_surf = _mk_surfaces()
    surf = Surface(main_surf)

    _fill_background_and_source(surf, src_surf)

    # set blend mode and draw source at a known location
    surf.blend_mode(mode)
    surf.image(src_surf, 10, 10)

    # sample an interior pixel of the source area
    px = surf.get_pixel(12, 12)

    # get_pixel returns (r,g,b) for non-SRCALPHA main surfaces
    assert isinstance(px, tuple)
    # allow equality to expected exact integer triple
    assert px[:3] == expected
