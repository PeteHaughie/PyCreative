"""
blend_subtract.py

Subtract blending demo (SUBTRACT).
"""

from pycreative.app import Sketch
from pycreative.graphics import Surface


class BlendSubtractSketch(Sketch):
    def setup(self):
        self.size(480, 240)
        self.set_title("Blend: SUBTRACT")
        self.no_stroke()

    def draw(self):
        self.clear((22, 22, 22))
        self.fill((40, 160, 200, 180))
        self.rect(60, 60, 200, 120)

        self.surface.blend_mode(Surface.SUBTRACT)
        self.fill((200, 50, 80, 180))
        self.rect(180, 30, 200, 120)


if __name__ == "__main__":
    BlendSubtractSketch().run()
