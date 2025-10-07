"""
blend_exclusion.py

Exclusion blending demo (EXCLUSION).
"""

from pycreative.app import Sketch
from pycreative.graphics import Surface


class BlendExclusionSketch(Sketch):
    def setup(self):
        self.size(480, 240)
        self.set_title("Blend: EXCLUSION")
        self.no_stroke()

    def draw(self):
        self.clear((12, 12, 12))
        self.fill((60, 120, 200, 200))
        self.rect(60, 60, 200, 120)

        self.surface.blend_mode(Surface.EXCLUSION)
        self.fill((200, 60, 120, 200))
        self.rect(180, 30, 200, 120)


if __name__ == "__main__":
    BlendExclusionSketch().run()
