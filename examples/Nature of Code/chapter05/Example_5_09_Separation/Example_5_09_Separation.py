"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_9_Separation/Example_5_9_Separation.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Separation
// Via Reynolds: http://www.red3d.com/cwr/steer/

// A simple model of flocking behavior where boids try to keep a certain distance from one another
"""

from pycreative.app import Sketch
from Vehicle import Vehicle


class Example_5_9_Separation(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 5.9: Separation")
        self.vehicles = [Vehicle(self, self.random(self.width), self.random(self.height)) for _ in range(25)]

    def update(self, dt):
        pass

    def draw(self):
        self.clear((255, 255, 255))
        for v in self.vehicles:
            v.separate(self.vehicles)
            v.update()
            v.borders()
            v.show()

    def mouse_dragged(self):
        x, y = self.mouse_x, self.mouse_y
        self.vehicles.append(Vehicle(self, x, y))
