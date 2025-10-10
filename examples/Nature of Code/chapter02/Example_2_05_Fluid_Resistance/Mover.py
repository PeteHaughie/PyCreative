"""
Mover class for simulating an object with mass, position, velocity, and acceleration.
"""


class Mover:
    def __init__(self, sketch, x=0, y=0, m=1.0):
        self.sketch = sketch
        self.mass = m
        self.radius = m * 8
        self.position = self.sketch.pvector(x, y)
        self.velocity = self.sketch.pvector(0, 0)
        self.acceleration = self.sketch.pvector(0, 0)

    def on_mass(self, new_value):
        self.mass = new_value
        self.radius = new_value * 8
        print("mass set to", self.mass, "radius set to", self.radius)

    def set_radius(self, new_value):
        self.mass = new_value / 8
        self.radius = new_value
        print("radius set to", self.radius, "mass set to", self.mass)

    def apply_force(self, force):
        f = self.sketch.pvector.div(force, self.mass)
        self.acceleration.add(f)

    def update(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)
        self.acceleration.mult(0)

    def draw(self):
        self.sketch.stroke((0, 0, 0))
        self.sketch.stroke_weight(2)
        self.sketch.fill((127, 127))
        self.sketch.circle(self.position.x, self.position.y, self.radius * 2)

    def check_edges(self):
        if self.position.y > self.sketch.height - self.radius:
            self.velocity.y *= -0.9  # A little dampening when hitting the bottom
            self.position.y = self.sketch.height - self.radius
