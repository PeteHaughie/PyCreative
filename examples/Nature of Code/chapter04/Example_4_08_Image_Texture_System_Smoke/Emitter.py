"""
Emitter class for Example 4.8: Image Texture System - Smoke
"""

from Particle import Particle


class Emitter:
    def __init__(self, sketch, x=0, y=0):
        self.sketch = sketch
        self.origin = self.sketch.pvector(x, y)
        self.particles = []

    def run(self):
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            particle.run()
            if particle.is_dead():
                self.particles.pop(i)

    def apply_force(self, force):
        for particle in self.particles:
            particle.apply_force(force)

    def add_particle(self):
        self.particles.append(Particle(self.sketch, self.origin.x, self.origin.y))
