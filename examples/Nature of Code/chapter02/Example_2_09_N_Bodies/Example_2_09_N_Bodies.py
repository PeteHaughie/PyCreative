"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter2/Example_2_9_N_Bodies/Example_2_9_N_Bodies.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 2.9: N Bodies
"""

from pycreative.app import Sketch
from Body import Body


class Example_2_09_N_Bodies(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("N Bodies Example")
        self.bodies = [Body(self, self.random(self.width), self.random(self.height), self.random(0.1, 2)) for _ in range(10)]
        self.G = 1

    def update(self, dt):
        pass

    def draw(self):
        self.clear((255, 255, 255))
        for i, body_i in enumerate(self.bodies):
            for j, body_j in enumerate(self.bodies):
                if i != j:
                    force = body_j.attract(self, body_i, self.G)
                    body_i.apply_force(self, force)
            body_i.update()
            body_i.draw(self)