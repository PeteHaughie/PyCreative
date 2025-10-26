"""
Particle class for Example 4-1: A Single Particle
"""


class Particle:
    def __init__(self, sketch, x = 0.0, y = 0.0):
        self.sketch = sketch
        self.position = self.sketch.pcvector(x, y)
        # For demonstration purposes the Particle has a random velocity.
        self.velocity = self.sketch.pcvector(self.sketch.random(-1, 1), self.sketch.random(-2, 0))
        self.acceleration = self.sketch.pcvector(0, 0)
        self.lifespan = 255.0

    def update(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)
        self.lifespan -= 2.0
        self.acceleration.mult(0)

    def draw(self):
        self.sketch.fill(self.lifespan, self.lifespan, self.lifespan)
        self.sketch.stroke(self.lifespan, self.lifespan, self.lifespan)
        self.sketch.stroke_weight(1)
        self.sketch.circle(self.position.x, self.position.y, 8)

    # Keeping the same physics model as with previous chapters
    def apply_force(self, force):
        self.acceleration.add(force)

    # Is the Particle alive or dead?
    def is_dead(self) -> bool:
        return self.lifespan < 0
