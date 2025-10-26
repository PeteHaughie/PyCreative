"""
Body class for Example 2-8: Two Body Attraction
"""


class Body:
    def __init__(self, sketch, x=0, y=0):
        self.sketch = sketch
        self.position = self.sketch.pcvector(x, y)
        self.velocity = self.sketch.pcvector(0, 0)
        self.acceleration = self.sketch.pcvector(0, 0)
        self.mass = 8
        self.r = (self.mass ** 0.5) * 2

    def attract(self, body):
        force = self.sketch.pcvector.sub(self.position, body.position)
        d = self.sketch.constrain(force.mag(), 5, 25)
        G = 1
        strength = (G * (self.mass * body.mass)) / (d * d)
        force.set_mag(strength)
        body.apply_force(force)

    def apply_force(self, force):
        f = self.sketch.pcvector.div(force, self.mass)
        self.acceleration.add(f)

    def update(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)
        self.acceleration.set(0, 0)

    def draw(self):
        self.sketch.stroke(0)
        self.sketch.stroke_weight(2)
        self.sketch.fill(127, 100, 100)
        self.sketch.ellipse(self.position.x, self.position.y, self.r * 4)
