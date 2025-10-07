"""
blend_screen.py

Screen blending demo (SCREEN).
"""

from pycreative.app import Sketch


class BlendScreenSketch(Sketch):
    def setup(self):
        self.size(480, 240)
        self.set_title("Blend: SCREEN")
        self.no_stroke()

    def draw(self):
        self.clear((16, 16, 16))
        self.fill((40, 40, 180, 180))
        self.rect(60, 60, 200, 120)

        self.blend_mode('SCREEN')
        self.fill((220, 40, 40, 180))
        self.rect(180, 30, 200, 120)


if __name__ == "__main__":
    BlendScreenSketch().run()
