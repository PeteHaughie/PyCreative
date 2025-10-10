"""
Oscillator object for Example 3-7: Oscillator Objects
"""


class Oscillator:
    def __init__(self, sketch):
        import random

        self.sketch = sketch
        self.angle = sketch.pvector(0, 0)
        self.angle_velocity = sketch.pvector(
            random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05)
        )
        self.amplitude = sketch.pvector(
            random.uniform(20, sketch.width / 2),
            random.uniform(20, sketch.height / 2),
        )

    def update(self):
        self.angle.add(self.angle_velocity)

    def draw(self):

        x = self.sketch.sin(self.angle.x) * self.amplitude.x
        y = self.sketch.sin(self.angle.y) * self.amplitude.y

        self.sketch.push()
        try:
            self.sketch.translate(self.sketch.width / 2, self.sketch.height / 2)
            self.sketch.stroke(0)
            self.sketch.stroke_weight(2)
            self.sketch.fill(127)
            self.sketch.line(0, 0, x, y)
            self.sketch.circle(x, y, 32)
        finally:
            self.sketch.pop()
