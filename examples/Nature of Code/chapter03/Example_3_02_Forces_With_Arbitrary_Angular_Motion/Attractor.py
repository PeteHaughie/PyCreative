"""
Attractor class for Example 3-2: Forces with Arbitrary Angular Motion
"""

class Attractor:
    def __init__(self, sketch, x: float = 0.0, y: float = 0.0, m: float = 20.0):
        self.sketch = sketch
        self.position = sketch.pcvector(x, y)
        self.mass = m
        self.G = 1.0

    def attract(self, mover):
        # Calculate direction of force
        force = self.position.copy().sub(mover.position)
        # Distance between objects
        distance = force.mag()
        # Limiting the distance to eliminate "extreme" results for very close or very far objects
        distance = self.sketch.constrain(distance, 5.0, 25.0)

        # Calculate gravitational force magnitude
        strength = (self.G * self.mass * mover.mass) / (distance * distance)
        # Get force vector --> magnitude * direction
        force.set_mag(strength)
        return force

    def display(self):
        self.sketch.ellipse_mode('CENTER')
        self.sketch.stroke(0)
        self.sketch.fill(175, 200, 200)
        self.sketch.circle(self.position.x, self.position.y, self.mass * 2)
