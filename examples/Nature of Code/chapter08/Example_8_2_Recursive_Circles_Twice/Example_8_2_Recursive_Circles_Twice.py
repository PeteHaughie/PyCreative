"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter8/Example_8_2_Recursive_Circles_Twice/Example_8_2_Recursive_Circles_Twice.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Simple Recursion
"""

from pycreative.app import Sketch


class Example_8_2_Recursive_Circles_Twice(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 8-2: Recursion Twice")
        self.no_loop()

    def draw(self):
        self.background(255)
        self.draw_circles(int(self.width / 2), int(self.height / 2), int(self.width / 2))

    def draw_circles(self, x: float, y: int, radius: float):
        self.stroke(0)
        self.stroke_weight(2)
        self.no_fill()
        self.circle(x, y, radius * 2)
        if radius > 4:
            # draw_circles() calls itself twice. For every circle, a smaller circle is drawn to the left and the right.
            self.draw_circles(x + radius / 2, y, radius / 2)
            self.draw_circles(x - radius / 2, y, radius / 2)
