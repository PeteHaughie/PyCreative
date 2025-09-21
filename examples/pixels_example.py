from pycreative import Sketch
from pycreative.pixels import Pixels


class PixelsGradientSketch(Sketch):
    def setup(self):
        self.size(400, 400)
        self.pixels = Pixels(self.width, self.height)
        # Fill with a horizontal grayscale gradient
        for x in range(self.width):
            for y in range(self.height):
                value = int(255 * (x / self.width))
                self.pixels.set(x, y, (value, value, value))
        self.surface = self.pixels.to_surface()

    def draw(self):
        import pygame

        pygame.display.get_surface().blit(self.surface, (0, 0))


if __name__ == "__main__":
    PixelsGradientSketch().run()
