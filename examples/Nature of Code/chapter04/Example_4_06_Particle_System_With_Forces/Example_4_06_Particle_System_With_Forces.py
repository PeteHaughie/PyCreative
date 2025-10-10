"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter4/Example_4_6_Particle_System_With_Forces/Example_4_6_Particle_System_With_Forces.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 4-6: Particle System with Forces
"""

from pycreative.app import Sketch
from Emitter import Emitter


class Example_4_06_Particle_System_With_Forces(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example_4_06_Particle_System_With_Forces")
        self.emitter = Emitter(self, self.width / 2, 50)

    def draw(self):
        self.no_stroke()
        self.fill(255, 30)
        self.rect(0, 0, self.width, self.height)

        gravity = self.pvector(0, 0.1)
        self.emitter.apply_force(gravity)

        self.emitter.add_particle()
        self.emitter.run()
