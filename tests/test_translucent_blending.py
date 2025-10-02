import pygame

from pycreative.graphics import Surface


def sample_pixel(surf, x, y):
    return surf.get_pixel(x, y)


def test_translucent_rect_blends(monkeypatch):
    # run headless
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    # Create a non-SRCALPHA surface to simulate main display
    main = pygame.Surface((50, 50))
    surf = Surface(main)

    # Fill background with solid blue
    surf.clear((0, 0, 255))

    # Draw a semi-transparent red rect in the center (alpha 128 out of 255)
    # Use fill as an RGBA tuple
    surf.rect(10, 10, 30, 30, fill=(255, 0, 0, 128))

    # Sample a pixel within the rect area
    px = sample_pixel(surf, 20, 20)

    # We expect blending: not pure red and not pure blue.
    assert isinstance(px, tuple)
    assert px != (255, 0, 0) and px != (0, 0, 255)