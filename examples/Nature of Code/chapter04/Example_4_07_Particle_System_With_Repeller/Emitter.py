"""
Emitter class for Example 4.7: Particle System with Repeller
"""

from Particle import Particle


class Emitter:
    def __init__(self, sketch, x, y):
        self.sketch = sketch
        self.origin = self.sketch.pvector(x, y)
        self.particles = []

    def add_particle(self):
        self.particles.append(Particle(self.sketch, self.origin.x, self.origin.y))

    def apply_force(self, force):
        for particle in self.particles:
            particle.apply_force(force)

    def apply_repeller(self, repeller):
        for particle in self.particles:
            force = repeller.repel(particle)
            particle.apply_force(force)

    def run(self):
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            particle.update()
            particle.run()
            if particle.is_dead():
                self.particles.pop(i)