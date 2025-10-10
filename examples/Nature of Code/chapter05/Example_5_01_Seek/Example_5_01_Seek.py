"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_1_Seek/Example_5_1_Seek.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Seeking "vehicle" follows the mouse position

// Example 5.1: Seek
"""

from pycreative.app import Sketch
from Vehicle import Vehicle


class Example_5_01_Seek(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 5.1: Seek")
        self.vehicle = Vehicle(self, self.width / 2, self.height / 2)

    def draw(self):
        self.clear(255)
        mouse = (self.mouse_x or 0, self.mouse_y or 0)

        # Draw an ellipse at the mouse position
        self.fill(127)
        self.stroke(0)
        self.stroke_weight(2)
        self.circle(mouse[0], mouse[1], 48)

        # Call the appropriate steering behaviors for our agents
        self.vehicle.seek(mouse)
        self.vehicle.update()
        self.vehicle.show()
