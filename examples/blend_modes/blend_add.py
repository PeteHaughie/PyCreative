"""
blend_add.py

Additive blending demo (ADD).
"""

from pycreative.app import Sketch


class BlendAddSketch(Sketch):
    def setup(self):
        self.size(480, 240)
        self.set_title("Blend: ADD")
        self.no_stroke()

    def draw(self):
        self.clear((20, 20, 20))
        self.fill((0, 100, 200, 160))
        self.rect(60, 60, 200, 120)
        self.blend_mode(self.ADD)
        self.fill((200, 60, 60, 160))
        self.rect(180, 30, 200, 120)


if __name__ == "__main__":
    BlendAddSketch().run()
