"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter4/Example_4_7_Particle_System_With_Repeller/Example_4_7_Particle_System_With_Repeller.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// One ParticleSystem

// Example 4-7: Particle System with Repeller
"""

from Emitter import Emitter
from Repeller import Repeller


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example_4_07 Particle_System_With_Repeller")
        self.emitter = Emitter(self, self.width / 2, 60)
        self.repeller = Repeller(self, self.width / 2, 250)

    def draw(self):
        self.background(255, 255, 255)
        self.emitter.add_particle()
        gravity = self.pcvector(0, 0.1)
        self.emitter.apply_force(gravity)
        self.emitter.apply_repeller(self.repeller)
        self.emitter.run()
        self.repeller.show()