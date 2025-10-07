"""
blend_lightest.py

Lightest blending demo (LIGHTEST).
"""

from pycreative.app import Sketch
from pycreative.graphics import Surface


class BlendLightestSketch(Sketch):
    def setup(self):
        self.size(480, 240)
        self.set_title("Blend: LIGHTEST")
        self.no_stroke()

    def draw(self):
        self.clear((14, 14, 14))
        self.fill((80, 120, 200, 180))
        self.rect(60, 60, 200, 120)

        self.surface.blend_mode(Surface.LIGHTEST)
        self.fill((200, 140, 80, 180))
        self.rect(180, 30, 200, 120)


if __name__ == "__main__":
    BlendLightestSketch().run()
