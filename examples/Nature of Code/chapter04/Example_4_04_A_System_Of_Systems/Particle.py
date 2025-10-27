"""
Particle class for Example 4.04: A System of Systems
"""

class Particle:
    def __init__(self, sketch, x=0.0, y=0.0):
        self.sketch = sketch
        self.position = self.sketch.pcvector(x, y)
        self.velocity = self.sketch.pcvector(self.sketch.random(-1, 1), self.sketch.random(-2, 0))
        self.acceleration = self.sketch.pcvector(0, 0)
        self.lifespan = 255.0

    def update(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)
        self.lifespan -= 2.0
        self.acceleration.mult(0)

    def draw(self):
        self.sketch.fill(255 - self.lifespan)
        self.sketch.stroke(255 - self.lifespan)
        self.sketch.stroke_weight(2)
        self.sketch.circle(self.position.x, self.position.y, 8)

    def apply_force(self, force):
        self.acceleration.add(force)

    def is_dead(self):
        return self.lifespan < 0.0
