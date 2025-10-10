"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter0/Example_0_1_Random_Walk/Example_0_1_Random_Walk.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 0-1: Random Walk
"""

from pycreative.app import Sketch

class Example_0_1_Random_Walk(Sketch):
    def setup(self):
        self.size(640, 360)
        self.walker_x = self.width // 2
        self.walker_y = self.height // 2
        self.background(255)  # White background

    def draw(self):
        self.stroke(0)  # Black stroke
        self.stroke_weight(1)
        self.point(self.walker_x, self.walker_y)
        choice = int(self.random(4))
        if choice == 0:
            self.walker_x += 1
        elif choice == 1:
            self.walker_x -= 1
        elif choice == 2:
            self.walker_y += 1
        else:
            self.walker_y -= 1
