"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter3/Example_3_2_Forces_With_Arbitrary_Angular_Motion/Example_3_2_Forces_With_Arbitrary_Angular_Motion.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 3-2: Forces with Arbitrary Angular Motion
"""

from pycreative.app import Sketch
from Attractor import Attractor
from Mover import Mover


class Example_3_02_Forces_With_Arbitrary_Angular_Motion(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 3.2: Forces with Arbitrary Angular Motion")
        self.movers = [Mover(self, self.random(self.width), self.random(self.height), self.random(0.1, 2.0)) for _ in range(20)]
        self.attractor = Attractor(self, self.width / 2, self.height / 2, 20.0)

    def update(self, dt):
        pass

    def draw(self):
        self.clear(255)
        self.attractor.display()
        for mover in self.movers:
            force = self.attractor.attract(mover)
            mover.apply_force(force)
            mover.update()
            mover.draw(self)
