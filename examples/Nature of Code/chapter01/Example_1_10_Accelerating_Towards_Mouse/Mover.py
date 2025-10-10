"""
Mover class for Example 1.10: Accelerating Towards Mouse
"""

class Mover:
    def __init__(self, sketch):
        self.sketch = sketch
        self.position = self.sketch.pvector(self.sketch.width / 2, self.sketch.height / 2)
        self.velocity = self.sketch.pvector(0, 0)
        self.acceleration = self.sketch.pvector(0, 0)
        self.topspeed = 5

    def update(self):
        mouse = self.sketch.pvector(self.sketch.mouse_x, self.sketch.mouse_y)
        # Step 1: Compute direction
        dir = self.sketch.pvector.sub(mouse, self.position)

        # Step 2: Normalize
        dir.normalize()

        # Step 3: Scale
        dir.mult(0.2)

        # Steps 2 and 3 could be combined into:
        # dir.setMag(0.2);

        # Step 4: Accelerate
        self.acceleration = dir

        self.velocity.add(self.acceleration)
        self.velocity.limit(self.topspeed)
        self.position.add(self.velocity)
        self.position.x = self.sketch.constrain(self.position.x, 0, self.sketch.width)
        self.position.y = self.sketch.constrain(self.position.y, 0, self.sketch.height)

    def draw(self):
        self.sketch.stroke((0, 0, 0))
        self.sketch.stroke_weight(2)
        self.sketch.fill(127)
        self.sketch.circle(self.position.x, self.position.y, 48)
