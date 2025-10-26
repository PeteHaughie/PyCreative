"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter2/Example_2_7_Attraction_With_Many_Movers/Example_2_7_Attraction_With_Many_Movers.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 2.7: Attraction with Many Movers
"""

from Attractor import Attractor
from Mover import Mover


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 2.7 Attraction with Many Movers")
        self.movers = [Mover(self, self.random(self.width), self.random(self.height), self.random(0.5, 3)) for _ in range(10)]
        self.attractor = Attractor(self, self.width / 2, self.height / 2)

    def update(self):
        for mover in self.movers:
            mover.update()

    def draw(self):
        self.background(255)
        self.attractor.show()

        for mover in self.movers:
            force = self.attractor.attract(mover)
            mover.apply_force(force)

            mover.show()

    def mouse_moved(self):
        self.attractor.handle_hover(self.mouse_x or 0, self.mouse_y or 0)

    def mouse_pressed(self):
        self.attractor.handle_press(self.mouse_x or 0, self.mouse_y or 0)

    def mouse_dragged(self):
        self.attractor.handle_hover(self.mouse_x or 0, self.mouse_y or 0)
        self.attractor.handle_drag(self.mouse_x or 0, self.mouse_y or 0)