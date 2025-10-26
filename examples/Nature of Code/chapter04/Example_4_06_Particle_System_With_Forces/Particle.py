"""
Particle class for Example 4.6: Particle System with Forces
"""


class Particle:
    def __init__(self, sketch, x=0.0, y=0.0):
        self.sketch = sketch
        self.position = self.sketch.pcvector(x, y)
        self.velocity = self.sketch.pcvector(self.sketch.random(-1, 1), self.sketch.random(-2, 0))
        self.acceleration = self.sketch.pcvector(0, 0)
        self.lifespan = 255.0
        self.mass = 1.0  # Let's do something better here!

    def draw(self):
        self.update()
        self.show()

    def apply_force(self, force):
        f = force.copy()
        f.div(self.mass)
        self.acceleration.add(f)

    def update(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)
        self.acceleration.mult(0)
        self.lifespan -= 2.0

    def show(self):
        self.sketch.stroke(self.lifespan, self.lifespan, self.lifespan)
        self.sketch.stroke_weight(2)
        self.sketch.fill(self.lifespan, self.lifespan, self.lifespan)
        self.sketch.ellipse(self.position.x, self.position.y, 8, 8)

    def is_dead(self):
        return self.lifespan < 0.0