"""
Mover class for Example 3-3: Pointing in the Direction of Motion
"""


class Mover:
    def __init__(self, sketch):
        self.sketch = sketch
        self.position = self.sketch.pvector(self.sketch.width / 2, self.sketch.height / 2)
        self.velocity = self.sketch.pvector(0, 0)
        self.acceleration = self.sketch.pvector(0, 0)
        self.topspeed = 4
        self.r = 16

    def update(self):
        mouse = self.sketch.pvector(self.sketch.mouse_x, self.sketch.mouse_y)
        dir = self.sketch.pvector.sub(mouse, self.position)
        dir.normalize()
        dir.mult(0.5)
        self.acceleration = dir

        self.velocity.add(self.acceleration)
        self.velocity.limit(self.topspeed)
        self.position.add(self.velocity)

    def draw(self):
        angle = self.velocity.heading()

        self.sketch.stroke(0)
        self.sketch.stroke_weight(2)
        self.sketch.fill(127)
        self.sketch.push()
        self.sketch.rect_mode(self.sketch.CENTER)

        self.sketch.translate(self.position.x, self.position.y)
        self.sketch.rotate(angle)
        self.sketch.rect(0, 0, 30, 10)

        self.sketch.pop()

    def check_edges(self):
        if self.position.x > self.sketch.width:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = self.sketch.width

        if self.position.y > self.sketch.height:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = self.sketch.height
