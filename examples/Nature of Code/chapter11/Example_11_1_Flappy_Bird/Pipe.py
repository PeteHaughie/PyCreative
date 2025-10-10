"""
Pip class for Example 11.1: Flappy Bird
"""

from random import uniform

class Pipe:
    def __init__(self, sketch):
        self.sketch = sketch
        self.spacing = 100
        self.top = uniform(0, self.sketch.height - self.spacing)
        self.bottom = self.top + self.spacing
        self.x = self.sketch.width
        self.w = 20
        self.velocity = 2

    def collides(self, bird):
        # Is the bird within the vertical range of the top or bottom pipe?
        vertical_collision = bird.y < self.top or bird.y > self.bottom
        # Is the bird within the horizontal range of the pipes?
        horizontal_collision = bird.x > self.x and bird.x < self.x + self.w
        # If it's both a vertical and horizontal hit, it's a hit!
        return vertical_collision and horizontal_collision

    def show(self):
        self.sketch.fill(0)
        self.sketch.no_stroke()
        self.sketch.rect(self.x, 0, self.w, self.top)
        self.sketch.rect(self.x, self.bottom, self.w, self.sketch.height - self.bottom)

    def update(self):
        self.x -= self.velocity

    def offscreen(self):
        return self.x < -self.w
