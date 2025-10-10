"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter2/Example_2_4_Including_Friction/Example_2_4_Including_Friction.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 2-4: Including Friction
"""

from pycreative.app import Sketch
from Mover import Mover


class Example_2_04_Including_Friction(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 2.4: Including Friction")
        self.mover = Mover(self, self.width / 2, 30, 5)
        self.mouse_is_pressed = False

    def draw(self):
        self.background(255)

        gravity = self.pvector(0, 1)
        # I should scale by mass to be more accurate, but this example only has one circle
        self.mover.apply_force(gravity)

        if self.mouse_is_pressed:
            wind = self.pvector(0.5, 0)
            self.mover.apply_force(wind)

        if self.mover.contact_edge():
            c = 0.1
            friction = self.mover.velocity.copy()
            friction.mult(-1)
            friction.set_mag(c)

            # Apply the friction force vector to the object.
            self.mover.apply_force(friction)

        self.mover.bounce_edges()
        self.mover.update()
        self.mover.draw()

    def mouse_pressed(self):
        self.mouse_is_pressed = True

    def mouse_released(self):
        self.mouse_is_pressed = False
