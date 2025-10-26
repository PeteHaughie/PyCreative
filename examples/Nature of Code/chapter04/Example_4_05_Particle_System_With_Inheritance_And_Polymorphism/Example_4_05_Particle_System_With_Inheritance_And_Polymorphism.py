"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter4/Example_4_5_Particle_System_With_Inheritance_And_Polymorphism/Example_4_5_Particle_System_With_Inheritance_And_Polymorphism.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 4-5: Particle System with Inheritance and Polymorphism
"""

from Emitter import Emitter


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example_4_05 Particle_System_With_Inheritance_And_Polymorphism")
        self.emitter = Emitter(self, self.width / 2, 50)

    def draw(self):
        self.background(255)
        self.emitter.add_particle()
        self.emitter.draw()
