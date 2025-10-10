"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter8/Example_8_1_Recursive_Circles_Once/Example_8_1_Recursive_Circles_Once.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Simple Recursion
"""

from pycreative.app import Sketch


class Example_8_01_Recursive_Circles_Once(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 8-1: Simple Recursion")
        self.no_loop()

    def draw(self):
        self.background(255)
        self.draw_circles(int(self.width / 2), int(self.height / 2), int(self.width / 2))

    def draw_circles(self, x: int, y: int, r: float):
        self.stroke(0)
        self.stroke_weight(2)
        self.circle(x, y, r * 2)
        # Exit condition, stop when radius is too small
        if r > 4:
            r *= 0.75
            # Call the function inside the function! (recursion!)
            self.draw_circles(x, y, r)
