"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter1/Example_1_10_Accelerating_Towards_Mouse/Example_1_10_Accelerating_Towards_Mouse.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 1-10: Accelerating towards the mouse
"""

from Mover import Mover


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("Example 1.10: Accelerating Towards Mouse")
        self.mover = Mover(self)

    def draw(self):
        self.background(255)
        self.mover.update()
        self.mover.draw()
