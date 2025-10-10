"""
Bird class for Example 11.1: Flappy Bird
"""

class Bird:
    def __init__(self, sketch):
        self.sketch = sketch
        # The bird's position (x will be constant)
        self.x = 50
        self.y = 120

        # Velocity and forces are scalar since the bird only moves along the y-axis
        self.velocity = 0.0
        self.gravity = 0.5
        self.flap_force = -10.0

    # The bird flaps its wings
    def flap(self):
        self.velocity += self.flap_force

    def update(self):
        # Add gravity
        self.velocity += self.gravity
        self.y += self.velocity
        # Dampen velocity
        self.velocity *= 0.95

        # Handle the "floor"
        if self.y > self.sketch.height:
            self.y = self.sketch.height
            self.velocity = 0.0

    def show(self):
        self.sketch.stroke_weight(2)
        self.sketch.stroke(0)
        self.sketch.fill(127)
        self.sketch.circle(self.x, self.y, 16)
