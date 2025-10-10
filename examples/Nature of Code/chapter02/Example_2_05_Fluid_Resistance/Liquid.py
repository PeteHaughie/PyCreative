"""
Liquid class for simulating fluid resistance in a 2D environment.
"""


class Liquid:
    def __init__(self, sketch, x=0.0, y=0.0, w=100.0, h=100.0, c=0.1):
        self.sketch = sketch
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.c = c

    def contains(self, mover):
        pos = mover.position
        return (pos.x > self.x and
                pos.x < self.x + self.w and
                pos.y > self.y and
                pos.y < self.y + self.h)

    def calculate_drag(self, mover):
        speed = mover.velocity.mag()
        drag_magnitude = self.c * speed * speed

        drag_force = mover.velocity.copy()
        drag_force.mult(-1)
        drag_force.set_mag(drag_magnitude)
        return drag_force

    def draw(self):
        self.sketch.no_stroke()
        self.sketch.fill((220, 220, 220))
        self.sketch.rect(self.x, self.y, self.w, self.h)
