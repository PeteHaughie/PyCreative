"""
blend_difference.py

Difference blending demo (DIFFERENCE).
"""

from pycreative.app import Sketch
from pycreative.graphics import Surface


class BlendDifferenceSketch(Sketch):
    def setup(self):
        self.size(480, 240)
        self.set_title("Blend: DIFFERENCE")
        self.no_stroke()

    def draw(self):
        self.clear((10, 10, 10))
        self.fill((20, 140, 220, 200))
        self.rect(60, 60, 200, 120)

        self.surface.blend_mode(Surface.DIFFERENCE)
        self.fill((220, 40, 40, 200))
        self.rect(180, 30, 200, 120)


if __name__ == "__main__":
    BlendDifferenceSketch().run()
