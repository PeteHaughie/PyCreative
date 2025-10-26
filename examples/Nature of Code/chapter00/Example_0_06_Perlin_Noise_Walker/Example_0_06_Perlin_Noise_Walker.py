"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter0/Example_0_6_Perlin_Noise_Walker/Example_0_6_Perlin_Noise_Walker.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 0-6: Perlin Noise Walker
"""


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 0-6 Perlin Noise Walker")
        self.background(255)
        self.walker = Walker(self)

    def draw(self):
        self.walker.update()
        self.walker.show()

class Walker:
    def __init__(self, sketch):
        self.sketch = sketch
        # Keep original Processing offsets but add a tiny fractional offset
        # to avoid starting at an exact lattice boundary which can produce
        # symmetric/biased derivatives in some Perlin implementations.
        self.tx = 0.0
        self.ty = 10000.0
        self.x = 0
        self.y = 0

    def update(self):
        # x- and y-position mapped from noise
        self.x = self.sketch.map(self.sketch.noise(self.tx), 0, 1, 0, self.sketch.width)
        self.y = self.sketch.map(self.sketch.noise(self.ty), 0, 1, 0, self.sketch.height)

        # Move forward through time.
        self.tx += 0.01
        self.ty += 0.01

    def show(self):
        self.sketch.stroke_weight(2)
        self.sketch.fill(127)
        self.sketch.stroke(0)
        self.sketch.circle(self.x, self.y, 48)
