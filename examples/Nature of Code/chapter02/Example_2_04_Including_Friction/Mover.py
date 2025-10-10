"""
Mover class for Example 2.4: Including Friction
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
        self.sketch.fill((127, 127, 127))
        self.sketch.ellipse(self.position.x, self.position.y, self.radius * 2)

    def contact_edge(self):
        return self.position.y > self.sketch.height - self.radius - 1

    def bounce_edges(self):
        bounce = -0.9
        if self.position.x > self.sketch.width - self.radius:
            self.position.x = self.sketch.width - self.radius
            self.velocity.x *= bounce
        elif self.position.x < self.radius:
            self.position.x = self.radius
            self.velocity.x *= bounce
        if self.position.y > self.sketch.height - self.radius:
            self.position.y = self.sketch.height - self.radius
            self.velocity.y *= bounce
