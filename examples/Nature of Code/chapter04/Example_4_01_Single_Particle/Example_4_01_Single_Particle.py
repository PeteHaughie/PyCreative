"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter4/Example_4_1_Single_Particle/Example_4_1_Single_Particle.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 4-1: Single Particle
"""

from pycreative.app import Sketch
from Particle import Particle


class Example_4_01_Single_Particle(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example_4_01_Single_Particle")
        self.particle = Particle(self, self.width / 2, 10)

    def draw(self):
        self.clear(255)
        # Operating the single Particle
        self.particle.update()
        self.particle.draw()

        # Applying a gravity force
        gravity = self.pvector(0, 0.1)
        self.particle.apply_force(gravity)

        # Checking the particle's state and making a new particle
        if self.particle.is_dead():
            self.particle = Particle(self, self.width / 2, 20)
