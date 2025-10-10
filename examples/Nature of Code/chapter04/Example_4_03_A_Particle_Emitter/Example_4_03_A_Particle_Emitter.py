"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter4/Example_4_3_A_Particle_Emitter/Example_4_3_A_Particle_Emitter.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 4-3: A Particle Emitter
"""

from pycreative.app import Sketch
from Emitter import Emitter


class Example_4_03_A_Particle_Emitter(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example_4_03_A_Particle_Emitter")
        self.emitter = Emitter(self, self.width / 2, 50)

    def update(self, dt):
        self.emitter.update()
        self.emitter.add_particle()

    def draw(self):
        self.clear(255)
        self.emitter.draw()