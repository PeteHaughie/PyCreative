"""
Emitter class for Example 4-5: Particle System with Inheritance and Polymorphism
"""

from Particle import Particle
from Confetti import Confetti


class Emitter:
    def __init__(self, sketch, x=0.0, y=0.0):
        self.sketch = sketch
        self.origin = self.sketch.pvector(x, y)
        self.particles = []

    def add_particle(self):
        r = self.sketch.random(1)
        if r < 0.5:
            self.particles.append(Particle(self.sketch, self.origin.x, self.origin.y))
        else:
            self.particles.append(Confetti(self.sketch, self.origin.x, self.origin.y))

    def draw(self):
        for i in range(len(self.particles) - 1, -1, -1):
            p = self.particles[i]
            p.draw()
            if p.is_dead():
                self.particles.pop(i)
