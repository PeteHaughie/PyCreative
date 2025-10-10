"""
Vehicle class for Example 5-10: Combining Seek and Separate
"""

from pycreative.vector import PVector


class Vehicle:
    def __init__(self, sketch, x=0, y=0):
        self.sketch = sketch
        self.position = self.sketch.pvector(x, y)
        self.velocity = self.sketch.pvector.random2d()
        self.acceleration = self.sketch.pvector(0, 0)
        self.r = 6.0
        self.maxspeed = 3.0  # Maximum speed
        self.maxforce = 0.2  # Maximum steering force

    def apply_behaviors(self, vehicles):
        separate_force = self.separate(vehicles)
        seek_force = self.seek(self.sketch.pvector(self.sketch.mouse_x or 0, self.sketch.mouse_y or 0))

        separate_force.mult(1.5)
        seek_force.mult(0.5)

        self.apply_force(separate_force)
        self.apply_force(seek_force)

    def apply_force(self, force):
        # We could add mass here if we want A = F / M
        self.acceleration.add(force)

    def separate(self, vehicles: list["Vehicle"]) -> "PVector":
        # Separation behavior: steer to avoid crowding local flockmates.
        desired_separation = self.r * 2
        sum = self.sketch.pvector(0, 0)
        count = 0
        # For every vehicle in the system, check if it's too close
        for other in vehicles:
            d = self.position.dist(other.position)
            # If the distance is greater than 0 and less than an arbitrary amount (0 when you are yourself)
            if self != other and d < desired_separation:
                # Calculate vector pointing away from neighbor
                diff = self.position.copy().sub(other.position)
                diff.set_mag(1 / d)  # Weight by distance
                sum.add(diff)
                count += 1  # Keep track of how many
        # Average -- divide by how many
        if count > 0:
            sum.div(count)
            # Our desired vector is the average scaled to maximum speed
            sum.set_mag(self.maxspeed)
            # Implement Reynolds: Steering = Desired - Velocity
            sum.sub(self.velocity)
            sum.limit(self.maxforce)
        return sum

    def seek(self, target):
        # A method that calculates a steering force towards a target
        desired = target.copy().sub(self.position)  # A vector pointing from the location to the target

        # Normalize desired and scale to maximum speed
        desired.normalize()
        desired.mult(self.maxspeed)
        # Steering = Desired minus velocity
        steer = desired.sub(self.velocity)
        steer.limit(self.maxforce)  # Limit to maximum steering force
        return steer

    def update(self):
        # Method to update location
        # Update velocity
        self.velocity.add(self.acceleration)
        # Limit speed
        self.velocity.limit(self.maxspeed)
        self.position.add(self.velocity)
        # Reset acceleration to 0 each cycle
        self.acceleration.mult(0)

    def borders(self):
        # Wraparound
        if self.position.x < -self.r:
            self.position.x = self.sketch.width + self.r
        if self.position.y < -self.r:
            self.position.y = self.sketch.height + self.r
        if self.position.x > self.sketch.width + self.r:
            self.position.x = -self.r
        if self.position.y > self.sketch.height + self.r:
            self.position.y = -self.r

    def show(self):
        self.sketch.stroke((0, 0, 0))
        self.sketch.stroke_weight(2)
        self.sketch.fill((127, 127, 127))
        self.sketch.push_matrix()
        try:
            self.sketch.translate(self.position.x, self.position.y)
            self.sketch.rotate(self.velocity.heading())
            self.sketch.begin_shape()
            self.sketch.vertex(self.r * 2, 0)
            self.sketch.vertex(-self.r * 2, -self.r)
            self.sketch.vertex(-self.r * 2, self.r)
            self.sketch.end_shape(close=True)
            # --- IGNORE ---
            # self.sketch.begin_shape()
            # self.sketch.vertex(self.r * 2, 0)
            # self.sketch.vertex(-self.r * 2, -self.r)
            # self.sketch.vertex(-self.r * 2, self.r)
            # self.sketch.end_shape()
            # --- IGNORE ---
        finally:
            self.sketch.pop_matrix()