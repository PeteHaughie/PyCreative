"""
blend_multiply.py

Multiply blending demo (MULTIPLY).
"""

from pycreative.app import Sketch
from pycreative.graphics import Surface


class BlendMultiplySketch(Sketch):
    def setup(self):
        self.size(480, 240)
        self.set_title("Blend: MULTIPLY")
        self.no_stroke()

    def draw(self):
        self.clear((18, 18, 18))
        self.fill((0, 140, 120, 200))
        self.rect(60, 60, 200, 120)

        self.surface.blend_mode(Surface.MULTIPLY)
        self.fill((220, 160, 60, 200))
        self.rect(180, 30, 200, 120)


if __name__ == "__main__":
    BlendMultiplySketch().run()
