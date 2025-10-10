"""
Repeller class for Example 4.7: Particle System with Repeller
"""


class Repeller:
    def __init__(self, sketch, x, y):
        self.sketch = sketch
        self.position = self.sketch.pvector(x, y)
        self.power = 150  # How strong is the repeller?

    def show(self):
        self.sketch.stroke(0)
        self.sketch.stroke_weight(2)
        self.sketch.fill((127, 127, 127))
        self.sketch.circle(self.position.x, self.position.y, 32)

    def repel(self, particle):
        force = self.sketch.pvector.sub(self.position, particle.position)
        distance = force.mag()
        distance = self.sketch.constrain(distance, 5, 50)
        strength = (-1 * self.power) / (distance * distance)
        force.set_mag(strength)
        return force