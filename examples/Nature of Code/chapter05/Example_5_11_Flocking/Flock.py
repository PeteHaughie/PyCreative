"""
Flock class for Example 5-11: Flocking
"""

class Flock:
    def __init__(self):
        self.boids = []

    def run(self):
        for boid in self.boids:
            boid.run(self.boids)

    def add_boid(self, b):
        self.boids.append(b)
