import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".." , "src"))

import pygame
import pytest

from pycreative.graphics import Surface, OffscreenSurface


@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_get_set_single_pixel(capsys):
    surf = pygame.Surface((4, 4))
    s = Surface(surf)
    s.clear((0, 0, 0))

    # set a pixel and read it back
    s.set(1, 1, (10, 20, 30))
    assert s.get(1, 1) == (10, 20, 30)

    # set out-of-bounds should print a hint but not raise
    s.set(-1, -1, (1, 2, 3))
    captured = capsys.readouterr()
    assert "out of bounds" in captured.out


def test_get_rect_clip_and_offscreen():
    surf = pygame.Surface((4, 4))
    s = Surface(surf)
    # paint a pattern: use coordinates
    for y in range(4):
        for x in range(4):
            s.set_pixel(x, y, (x * 10, y * 10, 0))

    # request a rect that extends beyond bounds -> clipped result
    sub = s.get(2, 2, 4, 4)
    assert isinstance(sub, OffscreenSurface)
    assert sub.raw.get_size() == (2, 2)
    # check one pixel value inside clipped region
    assert sub.get(0, 0) == s.get(2, 2)


def test_copy_scaled_and_blit():
    src_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
    src = Surface(src_surf)
    # draw a simple two-color pattern
    for y in range(4):
        for x in range(4):
            if x < 2:
                src.set_pixel(x, y, (255, 0, 0))
            else:
                src.set_pixel(x, y, (0, 255, 0))

    dest_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
    dest = Surface(dest_surf)
    dest.clear((0, 0, 0))

    # copy and scale source (4x4) into dest (8x8)
    dest.copy(src, 0, 0, 4, 4, 0, 0, 8, 8)

    # After scaling, top-left pixel should be red-ish (since left half was red)
    c = dest.get(0, 0)
    assert isinstance(c, tuple) and c[0] >= 200
