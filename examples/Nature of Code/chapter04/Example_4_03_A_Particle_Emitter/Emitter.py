"""
Particle Emitter class for Example 4-3: A Particle Emitter
"""

from Particle import Particle


class Emitter:
    def __init__(self, sketch, x=0.0, y=0.0):
        self.sketch = sketch
        self.origin = self.sketch.pvector(x, y)
        self.particles = []

    def update(self):
        for particle in self.particles:
            particle.update()

    def add_particle(self):
        self.particles.append(Particle(self.sketch, self.origin.x, self.origin.y))

    def draw(self):
        # Looping through backwards to delete
        for i in range(len(self.particles) - 1, -1, -1):
            self.particles[i].draw()
            if self.particles[i].is_dead():
                # Remove the particle
                self.particles.pop(i)
