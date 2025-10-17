"""
Mover class for Example 2.1: Forces
"""

class Mover:
    def __init__(self, sketch):
        self.sketch = sketch
        self.mass = 1
        self.position = self.sketch.pcvector(self.sketch.width // 2, 30)
        self.velocity = self.sketch.pcvector(0, 0)
        self.acceleration = self.sketch.pcvector(0, 0)

    def apply_force(self, force):
        f = self.sketch.pcvector.div(force, self.mass)
        self.acceleration.add(f)

    def update(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)
        self.acceleration.mult(0)

    def draw(self):
        self.sketch.stroke(0)
        self.sketch.stroke_weight(2)
        self.sketch.fill(127)
        self.sketch.ellipse(self.position.x, self.position.y, self.mass * 16)

    def check_edges(self):
        if self.position.x > self.sketch.width:
            self.position.x = self.sketch.width
            self.velocity.x *= -1
        elif self.position.x < 0:
            self.velocity.x *= -1
            self.position.x = 0
        if self.position.y > self.sketch.height:
            self.velocity.y *= -1
            self.position.y = self.sketch.height
