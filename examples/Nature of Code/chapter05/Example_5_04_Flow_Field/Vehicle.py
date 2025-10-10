"""
Flow Field class for Example 5-4: Flow Field
"""


class Vehicle:
    def __init__(self, sketch, x: float, y: float, ms: float, mf: float):
        self.sketch = sketch
        self.position = self.sketch.pvector(x, y)
        self.acceleration = self.sketch.pvector(0, 0)
        self.velocity = self.sketch.pvector(0, 0)
        self.r = 4
        self.maxspeed = ms
        self.maxforce = mf

    def run(self):
        self.update()
        self.borders()
        self.show()

    # Implementing Reynolds' flow field following algorithm
    # http://www.red3d.com/cwr/steer/FlowFollow.html
    def follow(self, flow):
        # What is the vector at that spot in the flow field?
        desired = flow.lookup(self.position)
        # Scale it up by maxspeed
        desired.mult(self.maxspeed)
        # Steering is desired minus velocity
        steer = desired - self.velocity
        steer.limit(self.maxforce)  # Limit to maximum steering force
        self.apply_force(steer)

    def apply_force(self, force):
        # We could add mass here if we want A = F / M
        self.acceleration += force

    # Method to update location
    def update(self):
        # Update velocity
        self.velocity += self.acceleration
        # Limit speed
        self.velocity.limit(self.maxspeed)
        self.position += self.velocity
        # Reset acceleration to 0 each cycle
        self.acceleration *= 0

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

    def show(self):
        # Draw a triangle rotated in the direction of velocity
        angle = self.velocity.heading()
        self.sketch.fill(127)
        self.sketch.stroke(0)
        self.sketch.stroke_weight(2)
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
