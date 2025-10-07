"""
blend_default.py

Simple demo showing the default (BLEND / source-over) behavior.
Run with: pycreative examples/blend_modes/blend_default.py
"""

from pycreative.app import Sketch


class BlendDefaultSketch(Sketch):
    def setup(self):
        self.size(480, 240)
        self.set_title("Blend: DEFAULT (BLEND)")
        self.no_stroke()

    def draw(self):
        self.clear((30, 30, 30))
        # background rectangle
        self.fill((0, 120, 255, 200))
        self.rect(60, 60, 200, 120)
        # ensure default blend mode
        self.blend_mode(self.BLEND)
        # overlapping translucent red
        self.fill((255, 80, 80, 180))
        self.rect(180, 30, 200, 120)


if __name__ == "__main__":
    BlendDefaultSketch().run()
