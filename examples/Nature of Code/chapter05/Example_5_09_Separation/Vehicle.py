"""
Vehicle class for Example 5-9: Separation
"""

class Vehicle:
    def __init__(self, sketch, x, y):
        self.sketch = sketch
        # All the usual stuff
        self.position = sketch.pvector(x, y)
        self.r = 12
        self.maxspeed = 3  # Maximum speed
        self.maxforce = 0.2  # Maximum steering force
        self.acceleration = sketch.pvector(0, 0)
        self.velocity = sketch.pvector(0, 0)

    def apply_force(self, force):
        # We could add mass here if we want A = F / M
        self.acceleration += force

    # Separation
    # Method checks for nearby vehicles and steers away
    def separate(self, vehicles):
        # {!1 .bold} Note how the desired separation is based
        # on the Vehicles size.
        desired_separation = self.r * 2
        sum_vector = self.sketch.pvector(0, 0)
        count = 0
        for other in vehicles:
            d = self.position.dist(other.position)
            if self != other and d < desired_separation:
                diff = self.position - other.position
                # {!1 .bold} What is the magnitude of the p5.Vector
                # pointing away from the other vehicle?
                # The closer it is, the more the vehicle should flee.
                # The farther, the less. So the magnitude is set
                # to be inversely proportional to the distance.
                diff.set_mag(1 / d)
                sum_vector += diff
                count += 1
        if count > 0:
            sum_vector.set_mag(self.maxspeed)
            steer = sum_vector - self.velocity
            steer.limit(self.maxforce)
            self.apply_force(steer)

    # Method to update location
    def update(self):
        # Update velocity
        self.velocity += self.acceleration
        # Limit speed
        self.velocity.limit(self.maxspeed)
        self.position += self.velocity
        # Reset acceleration to 0 each cycle
        self.acceleration *= 0

    def show(self):
        self.sketch.fill(127)
        self.sketch.stroke(0)
        self.sketch.stroke_weight(2)
        self.sketch.push_matrix()
        try:
            self.sketch.translate(self.position.x, self.position.y)
            self.sketch.circle(0, 0, self.r)
        finally:
            self.sketch.pop_matrix()

    # Wraparound
    def borders(self):
        if self.position.x < -self.r:
            self.position.x = self.sketch.width + self.r
        if self.position.y < -self.r:
            self.position.y = self.sketch.height + self.r
        if self.position.x > self.sketch.width + self.r:
            self.position.x = -self.r
        if self.position.y > self.sketch.height + self.r:
            self.position.y = -self.r
