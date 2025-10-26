"""
Body class for Example 2-9: N Bodies
"""


class Body:
    def __init__(self, sketch, x: float, y: float, m: float):        
        self.mass = m
        self.position = sketch.pcvector(x, y)
        self.velocity = sketch.pcvector(0, 0)
        self.acceleration = sketch.pcvector(0, 0)

    def apply_force(self, sketch, force):
        f = sketch.pcvector.div(force, self.mass)
        self.acceleration.add(f)

    def update(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)
        self.acceleration.mult(0)

    def draw(self, sketch):
        sketch.stroke(0)
        sketch.stroke_weight(2)
        sketch.fill(127)
        sketch.circle(self.position.x, self.position.y, self.mass * 16)

    def attract(self, sketch, other: "Body", G: float):
        # Calculate direction of force
        force = sketch.pcvector.sub(self.position, other.position)
        # Distance between objects
        distance = force.mag()
        # Limiting the distance to eliminate "extreme" results for very close or very far objects
        distance = max(5.0, min(distance, 25.0))

        # Calculate gravitional force magnitude
        strength = (G * self.mass * other.mass) / (distance * distance)
        # Get force vector --> magnitude * direction
        force.set_mag(strength)
        return force
