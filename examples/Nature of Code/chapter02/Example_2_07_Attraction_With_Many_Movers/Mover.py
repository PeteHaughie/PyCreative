"""
Mover class for Example 2.7: Attraction with Many Movers
"""

class Mover:
    def __init__(self, sketch, x=0.0, y=0.0, m=1.0):
        self.sketch = sketch
        self.mass = m
        self.radius = self.mass * 8
        self.position = self.sketch.pvector(x, y)
        self.velocity = self.sketch.pvector(1, 0)
        self.acceleration = self.sketch.pvector(0, 0)

    def apply_force(self, force):
        f = force / self.mass
        self.acceleration += f

    def update(self):
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0

    def draw(self):
        self.sketch.stroke(0)
        self.sketch.stroke_weight(2)
        self.sketch.fill((127, 127, 127))
        self.sketch.ellipse(self.position.x, self.position.y, self.radius * 2)
