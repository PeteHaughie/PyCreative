"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter8/Example_8_4_Cantor_Set/Example_8_4_Cantor_Set.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Cantor Set
// Renders a simple fractal, the Cantor Set
"""

from pycreative.app import Sketch


class Example_8_4_Cantor_Set(Sketch):
    def setup(self):
        self.size(640, 120)
        self.set_title("Example 8-4: Cantor Set")

    def draw(self):
        self.background(255)
        self.stroke(0)
        self.stroke_weight(2)
        # Call the recursive function
        self.cantor(10, 10, 620)
        self.no_loop()

    def cantor(self, x: float, y: int, length: float):
        # Stop at 1 pixel!
        if length > 1:
            self.line(x, y, x + length, y)
            self.cantor(x, y + 20, length / 3)
            self.cantor(x + (2 * length) / 3, y + 20, length / 3)
