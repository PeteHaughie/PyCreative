"""
Boid class for Example 5-11: Flocking
"""

class Boid:
    def __init__(self, sketch, x: float, y: float):
        self.sketch = sketch
        self.position = sketch.pvector(float(x), float(y))
        self.velocity = sketch.pvector(sketch.random(-1, 1), sketch.random(-1, 1))
        self.acceleration = sketch.pvector(0.0, 0.0)
        self.r = 3.0
        self.maxspeed = 3.0  # Maximum speed
        self.maxforce = 0.05  # Maximum steering force

    def run(self, boids: list["Boid"]):
        self.flock(boids)
        self.update()
        self.borders()
        self.show()

    def apply_force(self, force):
        # We could add mass here if we want A = F / M
        self.acceleration.add(force)

    # We accumulate a new acceleration each time based on three rules
    def flock(self, boids: list["Boid"]):
        sep = self.separate(boids)  # Separation
        ali = self.align(boids)  # Alignment
        coh = self.cohere(boids)  # Cohesion
        # Arbitrarily weight these forces
        sep.mult(1.5)
        ali.mult(1.0)
        coh.mult(1.0)
        # Add the force vectors to acceleration
        self.apply_force(sep)
        self.apply_force(ali)
        self.apply_force(coh)

    # Method to update location
    def update(self):
        # Update velocity
        self.velocity.add(self.acceleration)
        # Limit speed
        self.velocity.limit(self.maxspeed)
        self.position.add(self.velocity)
        # Reset accelertion to 0 each cycle
        self.acceleration.mult(0)

    # A method that calculates and applies a steering force towards a target
    def seek(self, target):
        desired = target.copy().sub(self.position)  # A vector pointing from the location to the target
        # Normalize desired and scale to maximum speed
        desired.normalize()
        desired.mult(self.maxspeed)
        # Steering = Desired minus Velocity
        steer = desired.sub(self.velocity)
        steer.limit(self.maxforce)  # Limit to maximum steering force
        return steer

    def show(self):
        # Draw a triangle rotated in the direction of velocity
        angle = self.velocity.heading()
        self.sketch.fill((127, 127, 127))
        self.sketch.stroke((0, 0, 0))
        self.sketch.push()
        try:
          self.sketch.translate(self.position.x, self.position.y)
          self.sketch.rotate(angle)
          self.sketch.begin_shape()
          self.sketch.vertex(self.r * 2, 0)
          self.sketch.vertex(-self.r * 2, -self.r)
          self.sketch.vertex(-self.r * 2, self.r)
          self.sketch.end_shape(close=True)
        finally:
          self.sketch.pop()

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

    # Separation
    # Method checks for nearby boids and steers away
    def separate(self, boids: list["Boid"]):
        desired_separation = 25.0
        steer = self.sketch.pvector(0.0, 0.0)
        count = 0
        # For every boid in the system, check if it's too close
        for other in boids:
            d = self.position.dist(other.position)
            # If the distance is greater than 0 and less than an arbitrary amount (0 when you are yourself)
            if 0 < d < desired_separation:
                # Calculate vector pointing away from neighbor
                diff = self.position.copy().sub(other.position)
                diff.normalize()
                diff.div(d)  # Weight by distance
                steer.add(diff)
                count += 1  # Keep track of how many
        # Average -- divide by how many
        if count > 0:
            steer.div(float(count))
        # As long as the vector is greater than 0
        if steer.mag() > 0:
            # Implement Reynolds: Steering = Desired - Velocity
            steer.normalize()
            steer.mult(self.maxspeed)
            steer.sub(self.velocity)
            steer.limit(self.maxforce)
        return steer

    # Alignment
    # For every nearby boid in the system, calculate the average velocity
    def align(self, boids: list["Boid"]):
        neighbor_distance = 50.0
        sum = self.sketch.pvector(0.0, 0.0)
        count = 0
        for other in boids:
            d = self.position.dist(other.position)
            if 0 < d < neighbor_distance:
                sum.add(other.velocity)
                count += 1
        if count > 0:
            sum.div(float(count))
            sum.normalize()
            sum.mult(self.maxspeed)
            steer = sum.sub(self.velocity)
            steer.limit(self.maxforce)
            return steer
        else:
            return self.sketch.pvector(0.0, 0.0)

    # Cohesion
    # For the average location (i.e. center) of all nearby boids, calculate steering vector towards that location
    def cohere(self, boids: list["Boid"]):
        neighbor_distance = 50.0
        sum = self.sketch.pvector(0.0, 0.0)  # Start with empty vector to accumulate all locations
        count = 0
        for other in boids:
            d = self.position.dist(other.position)
            if 0 < d < neighbor_distance:
                sum.add(other.position)  # Add location
                count += 1
        if count > 0:
            sum.div(float(count))
            return self.seek(sum)  # Steer towards the location
        else:
            return self.sketch.pvector(0.0, 0.0)
