"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter1/Example_1_8_Motion_101_Velocity_And_Constant_Acceleration/Example_1_8_Motion_101_Velocity_And_Constant_Acceleration.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 1-8: Motion 101: Velocity and Constant Acceleration
"""

from Mover import Mover


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("Example 1.8: Motion 101: Velocity and Constant Acceleration")
        self.mover = Mover(self)

    def draw(self):
        self.background(255)

        self.mover.update()
        self.mover.check_edges()
        self.mover.show()
