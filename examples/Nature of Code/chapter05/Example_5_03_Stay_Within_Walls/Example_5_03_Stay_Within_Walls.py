"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_3_Stay_Within_Walls/Example_5_3_Stay_Within_Walls.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Stay Within Walls
// "Made-up" Steering behavior to stay within walls
"""

from pycreative.app import Sketch
from Vehicle import Vehicle


class Example_5_03_Stay_Within_Walls(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 5.3: Stay Within Walls")
        self.vehicle = Vehicle(self, self.width / 2, self.height / 2)
        self.debug = True
        self.offset = 25

    def draw(self):
        self.clear(255)

        if self.debug:
            self.stroke(0)
            self.no_fill()
            self.rect_mode('CENTER')
            self.rect(self.width / 2, self.height / 2, self.width - self.offset * 2, self.height - self.offset * 2)

        # Call the appropriate steering behaviors for our agents
        self.vehicle.boundaries(self.offset)
        self.vehicle.update()
        self.vehicle.show()

    def mouse_pressed(self):
        self.debug = not self.debug
