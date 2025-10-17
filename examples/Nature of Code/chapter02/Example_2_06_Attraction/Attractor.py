"""
Attractor class for Example 2.6: Attraction
"""


class Attractor:
    def __init__(self, sketch, x, y, m=20):
        self.sketch = sketch
        self.position = self.sketch.pcvector(x, y)
        print(f"Creating attractor at {self.position.x}, {self.position.y}")
        self.mass = m
        self.drag_offset = self.sketch.pcvector(0, 0)
        self.dragging = False
        self.rollover = False

    def attract(self, mover):
        # Calculate direction of force
        force = self.sketch.pcvector.sub(self.position, mover.position)
        # Distance between objects
        distance = force.mag()
        # Limiting the distance to eliminate "extreme" results for very close or very far objects
        distance = self.sketch.constrain(distance, 5, 25)

        # Calculate gravitational force magnitude
        strength = (self.sketch.G * self.mass * mover.mass) / (distance * distance)
        # Get force vector --> magnitude * direction
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
            self.sketch.fill(175, 200, 175)
        # print(f"Drawing attractor at {self.position.x}, {self.position.y}")
        self.sketch.circle(self.position.x, self.position.y, self.mass * 2)

    def handle_press(self, mx: float, my: float):
        d = self.sketch.dist(mx, my, self.position.x, self.position.y)
        if d < self.mass:
            self.dragging = True
            self.drag_offset.x = self.position.x - mx
            self.drag_offset.y = self.position.y - my

    def handle_hover(self, mx: int, my: int):
        d = self.sketch.dist(mx, my, self.position.x, self.position.y)
        if d < self.mass:
            self.rollover = True
        else:
            self.rollover = False

    def stop_dragging(self):
        self.dragging = False

    def handle_drag(self, mx: float, my: float):
        if self.dragging:
            self.position.x = mx + self.drag_offset.x
            self.position.y = my + self.drag_offset.y
            # print(f"Dragging to {self.position.x}, {self.position.y}")
