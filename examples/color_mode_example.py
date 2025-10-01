"""Example demonstrating color_mode('HSB') usage.

Run with:
    python examples/color_mode_example.py
"""
from pycreative.app import Sketch


class ColorModeExample(Sketch):
    def setup(self):
        self.size(480, 240)
        self.set_title('Color Mode HSB Demo')
        # set HSB mode like Processing (h in 0..360, s/v in 0..100)
        self.color_mode('HSB', 360, 100, 100)
        self.no_stroke()

    def update(self, dt):
        pass

    def draw(self):
        self.clear((10, 10, 10))
        # draw a strip of hues
        for i in range(0, self.width, 4):
            for j in range(0, self.height, 4):
                h = int((i / self.width) * 360)
                # fill expects integer RGB/HSB components per type hints; cast hue to int
                self.fill((h, j, j))
                self.rect(i + 2, j + 2, 4, 4)


if __name__ == '__main__':
    ColorModeExample().run()
