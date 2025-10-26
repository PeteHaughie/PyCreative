"""
Attractor class for Example 2.7: Attraction with Many Movers
"""

class Attractor:
    def __init__(self, sketch, x, y, m=20):
        self.sketch = sketch
        self.position = self.sketch.pcvector(x, y)
        self.mass = m
        self.G = 1
        self.drag_offset = self.sketch.pcvector(0, 0)
        self.dragging = False
        self.rollover = False

    def attract(self, mover):
        force = self.position - mover.position
        distance = force.mag()
        distance = self.sketch.constrain(distance, 5, 25)
        strength = (self.G * self.mass * mover.mass) / (distance * distance)
        force.set_mag(strength)
        return force

    def show(self):
        self.sketch.stroke_weight(4)
        self.sketch.stroke(0)
        if self.dragging:
            self.sketch.fill(50)
        elif self.rollover:
            self.sketch.fill(100)
        else:
            self.sketch.fill(175, 200, 200)
        self.sketch.circle(self.position.x, self.position.y, self.mass * 2)

    def handle_press(self, mx, my):
        d = ((mx - self.position.x) ** 2 + (my - self.position.y) ** 2) ** 0.5
        if d < self.mass:
            self.dragging = True
            self.drag_offset.x = self.position.x - mx
            self.drag_offset.y = self.position.y - my

    def handle_hover(self, mx, my):
        d = ((mx - self.position.x) ** 2 + (my - self.position.y) ** 2) ** 0.5
        if d < self.mass:
            self.rollover = True
        else:
            self.rollover = False

    def stop_dragging(self):
        self.dragging = False

    def handle_drag(self, mx, my):
        if self.dragging:
            self.position.x = mx + self.drag_offset.x
            self.position.y = my + self.drag_offset.y