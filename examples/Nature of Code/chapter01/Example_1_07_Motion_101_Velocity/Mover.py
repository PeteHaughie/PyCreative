"""
Mover class for Example 1.7: Motion 101: Velocity
"""

class Mover:
    def __init__(self, sketch):
        self.sketch = sketch
        self.position = self.sketch.pvector(self.sketch.random(self.sketch.width), self.sketch.random(self.sketch.height))
        self.velocity = self.sketch.pvector(self.sketch.random(-2, 2), self.sketch.random(-2, 2))

    def update(self):
        self.position.add(self.velocity)

    def show(self):
        self.sketch.stroke((0, 0, 0))
        self.sketch.stroke_weight(2)
        self.sketch.fill(127)
        self.sketch.circle(self.position.x, self.position.y, 48)

    def checkEdges(self):
        if self.position.x > self.sketch.width:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = self.sketch.width

        if self.position.y > self.sketch.height:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = self.sketch.height