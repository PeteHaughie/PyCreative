"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter4/Example_4_1_Single_Particle/Example_4_1_Single_Particle.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 4-1: Single Particle
"""

from Particle import Particle


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example_4_01 Single_Particle")
        self.particle = Particle(self, self.width / 2, 10)

    def draw(self):
        self.background(255)
        # Operating the single Particle
        self.particle.update()
        self.particle.draw()

        # Applying a gravity force
        gravity = self.pcvector(0, 0.1)
        self.particle.apply_force(gravity)

        # Checking the particle's state and making a new particle
        if self.particle.is_dead():
            self.particle = Particle(self, self.width / 2, 20)
