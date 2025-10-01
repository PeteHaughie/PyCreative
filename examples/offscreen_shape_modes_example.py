"""Example: draw various shape modes into an offscreen surface and blit it.

Run with:
    python examples/offscreen_shape_modes_example.py

Or via the CLI to run headless or save frames:
    pycreative examples/offscreen_shape_modes_example.py --headless --max-frames 1
"""
from pycreative.app import Sketch


class OffscreenShapeModesExample(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Offscreen Shape Modes")
        # draw once by default for a static demo
        self.no_loop()

    def draw(self):
        # clear main canvas
        self.clear((18, 18, 24))

        # create an offscreen buffer and inherit current fill/stroke state
        g = self.create_graphics(420, 260, inherit_state=True)

        # background for offscreen (light gray)
        g.fill((40, 40, 48))
        g.begin_shape()
        g.vertex(0, 0)
        g.vertex(420, 0)
        g.vertex(420, 260)
        g.vertex(0, 260)
        g.end_shape()

        # red points
        g.stroke((220, 80, 80))
        g.stroke_weight(6)
        g.begin_shape('POINTS')
        for x in range(40, 380, 40):
            g.vertex(x, 30)
        g.end_shape()

        # green lines
        g.stroke((80, 220, 120))
        g.stroke_weight(3)
        g.begin_shape('LINES')
        g.vertex(30, 70)
        g.vertex(390, 70)
        g.vertex(30, 100)
        g.vertex(390, 100)
        g.end_shape()

        # blue triangle fan
        g.fill((90, 140, 220))
        g.begin_shape('TRIANGLE_FAN')
        g.vertex(210, 140)
        for a, b in ((120, 160), (160, 210), (260, 210), (300, 160)):
            g.vertex(a, b)
        g.end_shape()

        # orange quads
        g.fill((255, 160, 60))
        g.begin_shape('QUADS')
        g.vertex(40, 180)
        g.vertex(160, 180)
        g.vertex(160, 240)
        g.vertex(40, 240)
        g.vertex(260, 180)
        g.vertex(380, 180)
        g.vertex(380, 240)
        g.vertex(260, 240)
        g.end_shape()

        self.image(g.raw, 110, 50)
