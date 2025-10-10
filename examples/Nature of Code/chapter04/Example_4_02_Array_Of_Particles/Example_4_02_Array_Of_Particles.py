"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter4/Example_4_2_Array_Of_Particles/Example_4_2_Array_Of_Particles.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 4-2: Array of Particles
"""

from pycreative.app import Sketch
from Particle import Particle


class Example_4_02_Array_Of_Particles(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example_4_02_Array_Of_Particles")
        self.particles = []

    def draw(self):
        self.background(255)
        self.particles.append(Particle(self, self.width / 2, 20))

        # Looping through backwards to delete
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            particle.run()
            if particle.is_dead():
                # remove the particle
                self.particles.pop(i)
