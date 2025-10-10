"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_11_Flocking/Example_5_11_Flocking.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Demonstration of Craig Reynolds' "Flocking" behavior
// See: http://www.red3d.com/cwr/
// Rules: Cohesion, Separation, Alignment

// Click mouse to add boids into the system
"""

from pycreative.app import Sketch
from Flock import Flock
from Boid import Boid


class Example_5_11_Flocking(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 5.11: Flocking")
        self.flock = Flock()
        for _ in range(120):
            boid = Boid(self, (int)(self.width / 2), (int)(self.height / 2))
            self.flock.add_boid(boid)

    def update(self, dt: float = 0) -> None:
        self.flock.run()

    def draw(self):
        self.background((255, 255, 255))
        self.flock.run()

    def mouse_dragged(self):
        self.flock.add_boid(Boid(self, (int)(self.mouse_x or 0), (int)(self.mouse_y or 0)))
