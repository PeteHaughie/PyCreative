"""
Boid class for Example 5-12: Bin Lattice Spatial Separation
"""

class Boid:
    def __init__(self, sketch, x = 0, y = 0):
        self.sketch = sketch
        # Use sketch-provided pvector factory and don't create per-boid grid/resolution/cols/rows
        self.acceleration = self.sketch.pvector(0, 0)
        self.velocity = self.sketch.pvector(self.sketch.random(-1, 1), self.sketch.random(-1, 1))
        self.position = self.sketch.pvector(x, y)
        self.r = 3.0
        self.maxspeed = 3.0  # Maximum speed
        self.maxforce = 0.05  # Maximum steering force

    # No argument to run() anymore, use the sketch grid
    def run(self):
        # Defensive: ensure sketch has the grid and resolution
        try:
            resolution = self.sketch.resolution
            cols = self.sketch.cols
            rows = self.sketch.rows
            grid = self.sketch.grid
        except Exception:
            return

        # Compute cell indices based on this boid's position
        col = int(self.position.x // resolution)
        row = int(self.position.y // resolution)
        # Clamp to valid ranges
        col = max(0, min(col, cols - 1))
        row = max(0, min(row, rows - 1))

        neighbors: list[Boid] = []

        # Check cells in a 3x3 block around the current boid
        for i in range(-1, 2):
            for j in range(-1, 2):
                new_col = col + i
                new_row = row + j
                # Make sure this is a valid cell
                if 0 <= new_col < cols and 0 <= new_row < rows:
                    try:
                        cell = grid[new_row][new_col]
                        for b in cell:
                            # don't add self as neighbor
                            if b is not self:
                                neighbors.append(b)
                    except Exception:
                        # ignore malformed cells
                        pass

        self.flock(neighbors)
        self.update()
        self.borders()
        self.show()

    def apply_force(self, force):
        # We could add mass here if we want A = F / M
        self.acceleration.add(force)

    # We accumulate a new acceleration each time based on three rules
    def flock(self, boids: list):
        sep = self.separate(boids)  # Separation
        ali = self.align(boids)  # Alignment
        coh = self.cohesion(boids)  # Cohesion
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
    # STEER = DESIRED MINUS VELOCITY
    def seek(self, target):
        desired = self.sketch.pvector.sub(target, self.position)  # A vector pointing from the location to the target
        # Normalize desired and scale to maximum speed
        desired.normalize()
        desired.mult(self.maxspeed)
        # Steering = Desired minus Velocity
        steer = self.sketch.pvector.sub(desired, self.velocity)
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
    def separate(self, boids: list):
        desiredseparation = 25.0
        steer = self.sketch.pvector(0, 0)
        count = 0
        # For every boid in the system, check if it's too close
        for other in boids:
            d = self.sketch.pvector.dist(self.position, other.position)
            # If the distance is greater than 0 and less than an arbitrary amount (0 when you are yourself)
            if 0 < d < desiredseparation:
                # Calculate vector pointing away from neighbor
                diff = self.sketch.pvector.sub(self.position, other.position)
                diff.normalize()
                diff.div(d)  # Weight by distance
                steer.add(diff)
                count += 1  # Keep track of how many
        # Average -- divide by how many
        if count > 0:
            steer.div(count)

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
    def align(self, boids: list):
        neighbordist = 50
        sum = self.sketch.pvector(0, 0)
        count = 0
        for other in boids:
            d = self.sketch.pvector.dist(self.position, other.position)
            if 0 < d < neighbordist:
                sum.add(other.velocity)
                count += 1
        if count > 0:
            sum.div(count)
            sum.normalize()
            sum.mult(self.maxspeed)
            steer = self.sketch.pvector.sub(sum, self.velocity)
            steer.limit(self.maxforce)
            return steer
        else:
            return self.sketch.pvector(0, 0)

    # Cohesion
    # For the average location (i.e. center) of all nearby boids, calculate steering vector towards that location
    def cohesion(self, boids: list):
        neighbordist = 50

        sum = self.sketch.pvector(0, 0)  # Start with empty vector to accumulate all locations
        count = 0
        for other in boids:
            d = self.sketch.pvector.dist(self.position, other.position)
            if 0 < d < neighbordist:
                sum.add(other.position)  # Add location
                count += 1
        if count > 0:
            sum.div(count)
            return self.seek(sum)  # Steer towards the location
        else:
            return self.sketch.pvector(0, 0)
