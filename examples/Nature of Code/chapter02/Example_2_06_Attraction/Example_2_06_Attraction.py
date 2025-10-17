"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter2/Example_2_6_Attraction/Example_2_6_Attraction.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// A Mover and an Attractor
"""

from Attractor import Attractor
from Mover import Mover


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 2.6 Attraction")
        self.mover = Mover(self, 300, 50, 2)
        self.attractor = Attractor(self, self.width // 2, self.height // 2)
        self.G = 1  # gravitational constant (for global scaling)

    def draw(self):
        self.background(255)

        force = self.attractor.attract(self.mover)
        self.mover.apply_force(force)
        self.mover.update()

        self.attractor.show()
        self.mover.show()

    def mouse_moved(self):
        self.attractor.handle_hover(self.mouse_x or 0, self.mouse_y or 0)

    def mouse_pressed(self):
        self.attractor.handle_press(self.mouse_x or 0, self.mouse_y or 0)

    def mouse_dragged(self):
        self.attractor.handle_hover(self.mouse_x or 0, self.mouse_y or 0)
        self.attractor.handle_drag(self.mouse_x or 0, self.mouse_y or 0)

    def mouse_released(self):
        self.attractor.stop_dragging()
