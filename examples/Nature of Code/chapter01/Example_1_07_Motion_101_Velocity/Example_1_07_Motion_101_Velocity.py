"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter1/Example_1_7_Motion_101_Velocity/Example_1_7_Motion_101_Velocity.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com
"""

from Mover import Mover

class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("Example 1.7: Motion 101: Velocity")
        self.mover = Mover(self)

    def draw(self):
        self.background(255)

        self.mover.update()
        self.mover.checkEdges()
        self.mover.show()
