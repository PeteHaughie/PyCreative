"""
Flock class for Example 5-12: Bin Lattice Spatial Separation
"""

from Boid import Boid

class Flock:
    def __init__(self):
        self.boids: list[Boid] = []

    def run(self):
        for boid in self.boids:
            boid.run()

    def add_boid(self, boid):
        self.boids.append(boid)