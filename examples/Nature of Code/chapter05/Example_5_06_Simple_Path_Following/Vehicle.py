"""
Vehicle class for Example 5-6: Simple Path Following
"""

class Vehicle:
    def __init__(self, sketch, x, y, maxspeed, maxforce):
        self.sketch = sketch
        self.position = sketch.pvector(x, y)
        self.acceleration = sketch.pvector(0, 0)
        self.velocity = sketch.pvector(2, 0)
        self.r = 4
        self.maxspeed = maxspeed
        self.maxforce = maxforce
        self.debug = False

    def run(self):
        self.update()
        self.show()

    # This function implements Craig Reynolds' path following algorithm
    # http://www.red3d.com/cwr/steer/PathFollow.html
    def follow(self, path):
        # {!3} Step 1: Predict the vehicles future position.
        future = self.velocity.copy()
        future.set_mag(25)
        future += self.position

        # {!1} Step 2: Find the normal point along the path.
        normal_point = get_normal_point(self.sketch, future, path.start, path.end)

        # {!3} Step 3: Move a little further along the path and set a target.
        b = path.end - path.start
        b.set_mag(25)
        target = normal_point + b

        # {!5} Step 4: If we are off the path,
        # seek that target in order to stay on the path.
        distance = normal_point.dist(future)
        if distance > path.radius:
            self.seek(target)

        # Draw the debugging stuff
        if self.debug:
            self.sketch.fill(127)
            self.sketch.stroke(0)
            self.sketch.line(self.position.x, self.position.y, future.x, future.y)
            self.sketch.ellipse(future.x, future.y, 4, 4)

            # Draw normal location
            self.sketch.fill(127)
            self.sketch.stroke(0)
            self.sketch.line(future.x, future.y, normal_point.x, normal_point.y)
            self.sketch.ellipse(normal_point.x, normal_point.y, 4, 4)
            self.sketch.stroke(0)
            if distance > path.radius:
                self.sketch.fill(255, 0, 0)
            else:
                self.sketch.no_fill()
            self.sketch.circle(target.x + b.x, target.y + b.y, 8)
            self.sketch.no_stroke()

    def apply_force(self, force):
        # We could add mass here if we want A = F / M
        self.acceleration += force

    # A method that calculates and applies a steering force towards a target
    # STEER = DESIRED MINUS VELOCITY
    def seek(self, target):
        desired = target - self.position  # A vector pointing from the position to the target

        # If the magnitude of desired equals 0, skip out of here
        # (We could optimize this to check if x and y are 0 to avoid mag() square root
        if desired.mag() == 0:
            return

        # Normalize desired and scale to maximum speed
        desired.normalize()
        desired *= self.maxspeed
        # Steering = Desired minus Velocity
        steer = desired - self.velocity
        steer.limit(self.maxforce)  # Limit to maximum steering force

        self.apply_force(steer)

    def show(self):
        # Draw a triangle rotated in the direction of velocity
        theta = self.velocity.heading()
        self.sketch.fill(127)
        self.sketch.stroke(0)
        self.sketch.stroke_weight(2)
        self.sketch.push_matrix()
        try:
            self.sketch.translate(self.position.x, self.position.y)
            self.sketch.rotate(theta)
            self.sketch.begin_shape()
            self.sketch.vertex(self.r * 2, 0)
            self.sketch.vertex(-self.r * 2, -self.r)
            self.sketch.vertex(-self.r * 2, self.r)
            self.sketch.end_shape(close=True)
        finally:
            self.sketch.pop_matrix()

    def borders(self, path):
        if self.position.x > path.end.x + self.r:
            self.position.x = path.start.x - self.r
            self.position.y = path.start.y + (self.position.y - path.end.y)

    def update(self):
        # Update velocity
        self.velocity += self.acceleration
        # Limit speed
        self.velocity.limit(self.maxspeed)
        self.position += self.velocity
        # Reset acceleration to 0 each cycle
        self.acceleration *= 0

def get_normal_point(self, position, a, b):
    # Vector that points from a to position
    vector_a = position - a
    # Vector that points from a to b
    vector_b = b - a

    # Using the dot product for scalar projection
    vector_b.normalize()
    vector_b *= vector_a.dot(vector_b)
    # {!1} Finding the normal point along the line segment
    normal_point = a + vector_b
    return normal_point
