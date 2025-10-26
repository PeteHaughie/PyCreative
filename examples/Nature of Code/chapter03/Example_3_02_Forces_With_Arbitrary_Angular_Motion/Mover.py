"""
Mover class for Example 3-2: Forces with Arbitrary Angular Motion
"""


class Mover:
    def __init__(self, sketch, x = 0.0, y = 0.0, mass = 1.0):
        self.mass = mass
        self.radius = self.mass * 8
        self.position = sketch.pcvector(x, y)
        self.angle = 0.0
        self.angle_velocity = 0.0
        self.angle_acceleration = 0.0
        self.velocity = sketch.pcvector(sketch.random(-1, 1), sketch.random(-1, 1))
        self.acceleration = sketch.pcvector(0.0, 0.0)

    def apply_force(self, force):
        f = force / self.mass
        self.acceleration += f

    def update(self):
        self.velocity += self.acceleration
        self.position += self.velocity
        self.angle_acceleration = self.acceleration.x / 10.0
        self.angle_velocity += self.angle_acceleration
        self.angle_velocity = max(-0.1, min(0.1, self.angle_velocity))
        self.angle += self.angle_velocity
        self.acceleration *= 0.0

    def draw(self, sketch):
        sketch.stroke_weight(2)
        sketch.stroke(0)
        sketch.fill(127)
        sketch.rect_mode(sketch.CENTER)
        sketch.push_matrix()
        sketch.translate(self.position.x, self.position.y)
        sketch.rotate(self.angle)
        sketch.circle(0, 0, self.radius * 2)
        sketch.line(0, 0, self.radius, 0)
        sketch.pop_matrix()
