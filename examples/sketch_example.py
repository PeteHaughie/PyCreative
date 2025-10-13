# A minimal example of a PyCreative sketch

"""Self-contained example sketch.

This example defines a minimal Sketch class so it can be run directly in the
development layout without importing a legacy `pycreative.app`. The real
framework provides a richer `Sketch` in the installed package; this example
is intentionally tiny and demonstrates the CLI contract (a module-level
`Sketch` class with `setup` and `draw`).
"""

class Sketch:
    def setup(self):
        self.size(300, 200)
        # you can call self.background(...) here to request initial background
        self.no_loop()  # draw() runs just once

    def draw(self):
        self.fill(0)
        self.stroke(0, 0, 255)
        self.stroke_weight(3)
        self.square(20, 20, 100)  # square descriptor
        self.save_frame('out/sketch_example.png')
        print("Wrote out/sketch_example.png")