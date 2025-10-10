"""
Mover class for Example 2-6: Attraction
"""


class Mover:
    def __init__(self, sketch, x, y, m):
        self.sketch = sketch
        self.mass = m
        self.radius = m * 8
        self.position = self.sketch.pvector(x, y)
        self.velocity = self.sketch.pvector(0, 0)
        self.acceleration = self.sketch.pvector(0, 0)

    def apply_force(self, force):
        f = self.sketch.pvector.div(force, self.mass)
        self.acceleration.add(f)

    def update(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)
        self.acceleration.mult(0)

    def draw(self):
        self.sketch.stroke(0)
        self.sketch.stroke_weight(2)
        self.sketch.fill(127)
        self.sketch.ellipse(self.position.x, self.position.y, self.radius * 2)
