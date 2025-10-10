"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter1/Example_1_7_Motion_101_Velocity/Example_1_7_Motion_101_Velocity.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com
"""

from pycreative.app import Sketch
from Mover import Mover

class Example_1_7_Motion_101_Velocity(Sketch):
    def setup(self):
        self.size(640, 360)
        self.mover = Mover(self)

    def draw(self):
        self.background(255)

        self.mover.update()
        self.mover.checkEdges()
        self.mover.show()
