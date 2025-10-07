"""
blend_replace.py

Replace blending demo (REPLACE) — pixels from source overwrite destination.
"""

from pycreative.app import Sketch
from pycreative.graphics import Surface


class BlendReplaceSketch(Sketch):
    def setup(self):
        self.size(480, 240)
        self.set_title("Blend: REPLACE")
        self.no_stroke()

    def draw(self):
        self.clear((6, 6, 6))
        self.fill((80, 160, 200, 200))
        self.rect(60, 60, 200, 120)

        self.surface.blend_mode(Surface.REPLACE)
        self.fill((200, 40, 80, 200))
        self.rect(180, 30, 200, 120)


if __name__ == "__main__":
    BlendReplaceSketch().run()
