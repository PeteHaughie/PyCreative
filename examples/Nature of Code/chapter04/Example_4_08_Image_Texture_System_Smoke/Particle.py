"""
Particle class for Example 4.8: Image Texture System - Smoke
"""


class Particle:
    def __init__(self, sketch, x=0.0, y=0.0):
        self.sketch = sketch
        self.position = self.sketch.pcvector(x, y)
        vx = self.sketch.random_gaussian() * 0.3
        vy = (self.sketch.random_gaussian() * 0.3) - 1
        self.velocity = self.sketch.pcvector(vx, vy)
        self.acceleration = self.sketch.pcvector(0, 0)
        self.lifespan = 100.0

    def run(self):
        self.update()
        self.show()

    def apply_force(self, force):
        self.acceleration.add(force)

    def update(self):
        self.velocity.add(self.acceleration)
        self.position.add(self.velocity)
        self.lifespan -= 2
        self.acceleration.mult(0)

    def show(self):
        self.sketch.tint(255, self.lifespan)
        self.sketch.image_mode('CENTER')
        self.sketch.image(self.sketch.img, self.position.x, self.position.y)

    def is_dead(self):
        return self.lifespan < 0.0