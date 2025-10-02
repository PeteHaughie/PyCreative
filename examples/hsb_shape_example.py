"""HSB + shape modes example (Sketch idiom)

Shows using `color_mode('HSB', 360,100,100)` and drawing QUADS, TRIANGLE_FAN and POINTS.

Run with:
    python examples/hsb_shape_example.py

Or via the CLI:
    pycreative examples/hsb_shape_example.py --headless --max-frames 1
"""
from pycreative.app import Sketch


class HSBShapeExample(Sketch):
    def setup(self):
        self.size(520, 360)
        self.set_title("HSB Shape Modes Example")
        # we draw once for a static demo
        self.no_loop()

    def draw(self):
        # clear with dark background
        self.clear((12, 12, 16))

        # Set HSB color mode (h:0-360, s:0-100, b:0-100)
        self.color_mode('HSB', 360, 100, 100)

        # Big quad filled in HSB color
        self.fill((200, 70, 90))
        self.begin_shape('QUADS')
        self.vertex(30, 30)
        self.vertex(490, 30)
        self.vertex(490, 160)
        self.vertex(30, 160)
        self.end_shape()

        # Triangle fan with a different HSB hue
        self.fill((120, 60, 95))
        self.begin_shape('TRIANGLE_FAN')
        self.vertex(260, 210)
        self.vertex(180, 240)
        self.vertex(220, 310)
        self.vertex(300, 310)
        self.vertex(340, 240)
        self.end_shape()

        # Points using stroke (preferred for POINTS mode)
        self.no_fill()
        self.stroke((280, 90, 90))
        self.stroke_weight(8)
        self.begin_shape('POINTS')
        for x in range(60, 460, 40):
            self.vertex(x, 200)
        self.end_shape()


if __name__ == '__main__':
    HSBShapeExample().run()
