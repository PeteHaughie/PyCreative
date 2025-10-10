"""
Vehicle class for Example 5-3: Stay Within Walls
"""


class Vehicle:
    def __init__(self, sketch, x: float, y: float):
        self.sketch = sketch
        self.position = self.sketch.pvector(x, y)
        self.velocity = self.sketch.pvector(3, 4)
        self.acceleration = self.sketch.pvector(0, 0)
        self.r = 6
        self.maxspeed = 3
        self.maxforce = 0.15

    # Method to update location
    def update(self):
        # Update velocity
        self.velocity += self.acceleration
        # Limit speed
        self.velocity.limit(self.maxspeed)
        self.position += self.velocity
        # Reset acceleration to 0 each cycle
        self.acceleration *= 0

    def apply_force(self, force):
        # We could add mass here if we want A = F / M
        self.acceleration += force

    def boundaries(self, offset):
        desired = None

        if self.position.x < offset:
            desired = self.sketch.pvector(self.maxspeed, self.velocity.y)
        elif self.position.x > self.sketch.width - offset:
            desired = self.sketch.pvector(-self.maxspeed, self.velocity.y)

        if self.position.y < offset:
            desired = self.sketch.pvector(self.velocity.x, self.maxspeed)
        elif self.position.y > self.sketch.height - offset:
            desired = self.sketch.pvector(self.velocity.x, -self.maxspeed)

        if desired is not None:
            desired.normalize()
            desired.mult(self.maxspeed)
            steer = desired - self.velocity
            steer.limit(self.maxforce)
            self.apply_force(steer)

    # A method that calculates a steering force towards a target
    # STEER = DESIRED MINUS VELOCITY
    def show(self):
        # Vehicle is a triangle pointing in the direction of velocity
        angle = self.velocity.heading()
        self.sketch.fill(127)
        self.sketch.stroke(0)
        self.sketch.stroke_weight(3)
        self.sketch.push_matrix()
        try:
            self.sketch.translate(self.position.x, self.position.y)
            self.sketch.rotate(angle)
            self.sketch.begin_shape('POLYGON')
            self.sketch.vertex(self.r * 2, 0)
            self.sketch.vertex(-self.r * 2, -self.r)
            self.sketch.vertex(-self.r * 2, self.r)
            self.sketch.end_shape(close=True)
        finally:
            self.sketch.pop_matrix()
