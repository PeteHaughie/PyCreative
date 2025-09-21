# Pixels Class API (pycreative.pixels)

## Overview
`pycreative.pixels` provides the `Pixels` utility class for creating and manipulating pixel arrays and images in PyCreative sketches.

## Pixels Class
```python
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
```

## Usage Example
```python
pixels = Pixels(320, 240)
pixels.fill((0, 0, 0))
pixels.set(10, 10, (255, 0, 0))
surface = pixels.to_surface()
```

---
For more details, see `src/pycreative/pixels.py`.
