"""
blend_darkest.py

Darkest blending demo (DARKEST).
"""

from pycreative.app import Sketch
from pycreative.graphics import Surface


class BlendDarkestSketch(Sketch):
    def setup(self):
        self.size(480, 240)
        self.set_title("Blend: DARKEST")
        self.no_stroke()

    def draw(self):
        self.clear((8, 8, 8))
        self.fill((60, 160, 100, 160))
        self.rect(60, 60, 200, 120)

        self.surface.blend_mode(Surface.DARKEST)
        self.fill((200, 80, 140, 160))
        self.rect(180, 30, 200, 120)


if __name__ == "__main__":
    BlendDarkestSketch().run()
