"""
Vehicle class for Example 5.1: Seek
"""


class Vehicle:
    def __init__(self, sketch, x: float, y: float):
        self.sketch = sketch
        self.position = self.sketch.pvector(x, y)
        self.velocity = self.sketch.pvector(0, 0)
        self.acceleration = self.sketch.pvector(0, 0)
        self.r = 6
        self.maxspeed = 8
        self.maxforce = 0.2

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

    # A method that calculates a steering force towards a target
    # STEER = DESIRED MINUS VELOCITY
    def seek(self, target):
        desired = target - self.position  # A vector pointing from the location to the target

        # Scale to maximum speed
        desired.set_mag(self.maxspeed)

        # Steering = Desired minus velocity
        steer = desired - self.velocity
        steer.limit(self.maxforce)  # Limit to maximum steering force

        self.apply_force(steer)

    def show(self):
        # Vehicle is a triangle pointing in the direction of velocity
        angle = self.velocity.heading()
        self.sketch.fill(127)
        self.sketch.stroke(0)
        self.sketch.push_matrix()
        try:
            self.sketch.translate(self.position.x, self.position.y)
            self.sketch.rotate(angle)
            self.sketch.begin_shape('POLYGON')
            self.sketch.vertex(self.r * 2, 0)
            self.sketch.vertex(-self.r * 2, -self.r)
            self.sketch.vertex(-self.r * 2, self.r)
            self.sketch.end_shape()
        finally:
            self.sketch.pop_matrix()