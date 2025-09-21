"""
pycreative.pixels: Pixel array and image generation utilities for creative coding.
"""

from typing import Tuple

import numpy as np
import pygame


class Pixels:
    """
    Utility class for creating and manipulating pixel arrays and images.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.array = np.zeros((height, width, 3), dtype=np.uint8)

    def set(self, x: int, y: int, color: Tuple[int, int, int]):
        self.array[y, x] = color

    def get(self, x: int, y: int) -> Tuple[int, int, int]:
        return tuple(self.array[y, x])

    def fill(self, color: Tuple[int, int, int]):
        self.array[:, :] = color

    def to_surface(self) -> pygame.Surface:
        """
        Convert the pixel array to a pygame.Surface.
        """
        return pygame.surfarray.make_surface(self.array.swapaxes(0, 1))
