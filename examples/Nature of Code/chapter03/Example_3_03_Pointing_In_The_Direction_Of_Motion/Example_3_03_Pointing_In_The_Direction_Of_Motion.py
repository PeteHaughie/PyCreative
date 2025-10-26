"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter3/Example_3_3_Pointing_In_The_Direction_Of_Motion/Example_3_3_Pointing_In_The_Direction_Of_Motion.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 3-3: Pointing in the Direction of Motion
"""

from Mover import Mover


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("Example 3.3: Pointing in the Direction of Motion")
        self.mover = Mover(self)

    def update(self, dt):
        self.mover.update()

    def draw(self):
        self.background(255)
        self.mover.check_edges()
        self.mover.draw()
