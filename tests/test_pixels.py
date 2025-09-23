"""
Unit tests for pycreative.pixels.Pixels class.
"""

import numpy as np
import pygame
from pycreative.pixels import Pixels


def test_pixels_init():
    p = Pixels(10, 5)
    assert p.width == 10
    assert p.height == 5
    assert isinstance(p.array, np.ndarray)
    assert p.array.shape == (5, 10, 3)


def test_pixels_set_and_get():
    p = Pixels(4, 4)
    p.set(2, 1, (123, 45, 67))
    assert p.get(2, 1) == (123, 45, 67)


def test_pixels_fill():
    p = Pixels(3, 2)
    p.fill((10, 20, 30))
    for y in range(2):
        for x in range(3):
            assert p.get(x, y) == (10, 20, 30)


def test_pixels_to_surface():
    p = Pixels(2, 2)
    p.fill((255, 0, 0))
    surf = p.to_surface()
    assert isinstance(surf, pygame.Surface)
    assert surf.get_size() == (2, 2)
