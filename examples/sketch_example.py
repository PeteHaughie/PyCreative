"""Self-contained example sketch.

This example defines a minimal Sketch class so it can be run directly in the
development layout without importing a legacy `pycreative.app`. The real
framework provides a richer `Sketch` in the installed package; this example
is intentionally tiny and demonstrates the CLI contract (a module-level
`Sketch` class with `setup` and `draw`).
"""


class Sketch:
    def setup(self):
        print("setup called")
        self.size(600, 400)
        self.window_title("Sketch Example")
        # you can call self.background(...) here to request initial background
        # make the square visually distinct from the red background
        # self.background(0, 255, 0)
        self.x = 0
        self.frame_rate(60)
        # self.no_loop()  # draw() runs just once

    def draw(self):
        print("draw called")
        # self.background(0, 255, 0)
        # self.fill(255, 0, 0)
        self.rect(10, 10, 100, 200)
        self.circle(200 + self.x, 10, 50)
        print("self.x:", self.x)
        self.x += 1
        # self.fill(0, 255, 0)
        # self.stroke(0, 0, 255)
        # self.stroke_weight(3)
        # draw a larger square near the center so it's easy to see
        # self.square(250, 150, 300)
        # optional: save a snapshot (requires Pillow or a snapshot backend)
        # self.save_frame('out/sketch_example.png')
