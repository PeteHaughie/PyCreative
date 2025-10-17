"""
Mover class for Example 2.3: Gravity Scaled by Mass
"""


class Mover():
    def __init__(self, sketch, x=0, y=0, m=1):
        self.sketch = sketch
        self.mass = m
        self.radius = self.mass * 8
        self.position = self.sketch.pcvector(x, y)
        self.velocity = self.sketch.pcvector(0, 0)
        self.acceleration = self.sketch.pcvector(0, 0)

    def apply_force(self, force):
        f = self.sketch.pcvector.div(force, self.mass)
        self.acceleration.add(f)

    def update(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)
        self.acceleration.mult(0)

    def show(self):
        self.sketch.stroke(0)
        self.sketch.stroke_weight(2)
        self.sketch.fill(127)
        self.sketch.circle(self.position.x, self.position.y, self.radius * 2)

    def check_edges(self):
        if self.position.x > self.sketch.width - self.radius:
            self.position.x = self.sketch.width - self.radius
            self.velocity.x *= -1
        elif self.position.x < self.radius:
            self.position.x = self.radius
            self.velocity.x *= -1
        if self.position.y > self.sketch.height - self.radius:
            self.position.y = self.sketch.height - self.radius
            self.velocity.y *= -1
