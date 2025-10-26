"""
Emitter class for a particle system.
"""

from Particle import Particle


class Emitter:
    def __init__(self, sketch, x=0.0, y=0.0):
        self.sketch = sketch
        self.origin = self.sketch.pcvector(x, y)
        self.particles = []

    def add_particle(self):
        self.particles.append(Particle(self.sketch, self.origin.x, self.origin.y))

    def update(self):
        for particle in self.particles:
            particle.update()

    def draw(self):
        # Looping through backwards to delete
        for i in range(len(self.particles) - 1, -1, -1):
            self.particles[i].draw()
            if self.particles[i].is_dead():
                # Remove the particle
                self.particles.pop(i)
