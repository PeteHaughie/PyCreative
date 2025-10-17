"""
Mover class for Example 1.8: Motion 101: Velocity and Constant Acceleration
"""

class Mover:
    def __init__(self, sketch):
        self.sketch = sketch
        self.position = self.sketch.pcvector(self.sketch.width / 2, self.sketch.height / 2)
        self.velocity = self.sketch.pcvector(0, 0)
        self.acceleration = self.sketch.pcvector(-0.001, 0.01)
        self.top_speed = 10

    def update(self):
        self.velocity.add(self.acceleration)
        self.velocity.limit(self.top_speed)
        self.position.add(self.velocity)

    def show(self):
        self.sketch.stroke((0, 0, 0))
        self.sketch.stroke_weight(2)
        self.sketch.fill(127)
        self.sketch.circle(self.position.x, self.position.y, 48)

    def check_edges(self):
        if self.position.x > self.sketch.width:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = self.sketch.width

        if self.position.y > self.sketch.height:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = self.sketch.height
