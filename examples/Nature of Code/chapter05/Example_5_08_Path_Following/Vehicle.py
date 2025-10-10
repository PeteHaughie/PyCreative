"""
Vehicle class for Example 5-8: Path Following
"""

class Vehicle:
    def __init__(self, sketch, x, y, maxspeed=4, maxforce=0.1):
        self.sketch = sketch
        self.position = sketch.pvector(x, y)
        self.acceleration = sketch.pvector(0, 0)
        self.velocity = sketch.pvector(2, 0)
        self.r = 4
        self.maxspeed = maxspeed  # || 4;
        self.maxforce = maxforce  # || 0.1;
        self.debug = False

    def run(self):
        self.update()
        self.show()

    # This function implements Craig Reynolds' path following algorithm
    # http://www.red3d.com/cwr/steer/PathFollow.html
    def follow(self, path):
        """
        Predicts the vehicle's future position and steers it to follow a given path.

        The method works by projecting the vehicle's current velocity forward to estimate a future position.
        It then finds the closest point (normal) on the path to this predicted position by checking each segment
        of the path. If the predicted position is farther from the path than the path's radius, the vehicle will
        steer towards a target point slightly ahead of the closest normal point.

        Args:
          path: An object representing the path to follow. It must have:
            - points: a list of vector-like objects with x and y attributes.
            - radius: a float representing the path's radius.

        Attributes Used:
          self.position: Current position vector of the vehicle.
          self.velocity: Current velocity vector of the vehicle.
          self.debug: Boolean flag to enable debug drawing.
          self.sketch: Drawing context for debug visualization.

        Notes:
          - The target variable is a vector-like object with x and y attributes (e.g., a custom Vector class).
          - The method assumes path points are ordered and the path is traversed left to right.
          - For linters, you may use type hints or comments to indicate that 'target' is a vector-like object:
            target: Vector  # where Vector has x and y attributes
        """
        # Predict location 50 (arbitrary choice) frames ahead
        # This could be based on speed
        future = self.velocity.copy()
        future.set_mag(50)
        future += self.position

        # Now we must find the normal to the path from the predicted location
        # We look at the normal for each line segment and pick out the closest one
        # how do we tell the linter that target is an xy vector?
        target = None
        normal = None
        dir = None  # Ensure dir is always defined
        world_record = float('inf')  # Start with a very high record distance that can easily be beaten

        # Loop through all points of the path
        for i in range(len(path.points) - 1):
            # Look at a line segment
            a = path.points[i]
            b = path.points[i + 1]

            # Get the normal point to that line
            normal_point = self.get_normal_point(future, a, b)
            # This only works because we know our path goes from left to right
            # We could have a more sophisticated test to tell if the point is in the line segment or not
            if normal_point.x < a.x or normal_point.x > b.x:
                # This is something of a hacky solution, but if it's not within the line segment
                # consider the normal to just be the end of the line segment (point b)
                normal_point = b.copy()

            # How far away are we from the path?
            distance = future.dist(normal_point)
            # Did we beat the record and find the closest line segment?
            if distance < world_record:
                world_record = distance
                # If so the target we want to steer towards is the normal
                normal = normal_point
                target = normal_point.copy()
                # Look at the direction of the line segment so we can seek a little bit ahead of the normal
                dir = b - a
                # This is an oversimplification
                # Should be based on distance to path & velocity
                dir.set_mag(10)
                target += dir
        # Only if the distance is greater than the path's radius do we bother to steer
        if world_record > path.radius and target is not None:
            self.seek(target) # seek(target)
        # Draw the debugging stuff
        if self.debug:
            # Draw predicted future location
            self.sketch.stroke(0)
            self.sketch.fill(127)
            self.sketch.line(self.position.x, self.position.y, future.x, future.y)
            self.sketch.ellipse(future.x, future.y, 4, 4)

            # Draw normal location
            if normal is not None:
                self.sketch.stroke(0)
                self.sketch.fill(127)
                self.sketch.circle(normal.x, normal.y, 4)
                # Draw actual target (red if steering towards it)
                self.sketch.line(future.x, future.y, normal.x, normal.y)
                if world_record > path.radius:
                    self.sketch.fill(255, 0, 0)
                self.sketch.no_stroke()
                if target is not None:
                    self.sketch.circle(target.x, target.y, 8)
                self.sketch.no_stroke()
                self.sketch.no_fill()
                if target is not None and dir is not None:
                    self.sketch.circle(target.x + dir.x, target.y + dir.y, 8)
                    self.sketch.circle(target.x + dir.x, target.y + dir.y, 8)

    def apply_force(self, force):
        # We could add mass here if we want A = F / M
        self.acceleration += force

    # A method that calculates and applies a steering force towards a target
    # STEER = DESIRED MINUS VELOCITY
    def steer_towards(self, target):
        desired = target - self.position
        desired.set_mag(self.maxspeed)
        steer = desired - self.velocity
        steer.limit(self.maxforce)
        self.apply_force(steer)

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

    # Method to update position
    def update(self):
        # Update velocity
        self.velocity += self.acceleration
        # Limit speed
        self.velocity.limit(self.maxspeed)
        self.position += self.velocity
        # Reset accelerationelertion to 0 each cycle
        self.acceleration *= 0

    # Wraparound
    def borders(self, path):
        if self.position.x > path.get_end().x + self.r:
            self.position.x = path.get_start().x - self.r
            self.position.y = path.get_start().y + (self.position.y - path.get_end().y)

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

    # A function to get the normal point from a point (p) to a line segment (a-b)
    # This function could be optimized to make fewer new Vector objects
    def get_normal_point(self, position, a, b):
        # Vector from a to p
        vector_a = position - a
        # Vector from a to b
        vector_b = b - a
        vector_b.normalize()  # Normalize the line
        # Project vector "diff" onto line by using the dot product
        vector_b *= vector_a.dot(vector_b)
        normal_point = a + vector_b
        return normal_point
