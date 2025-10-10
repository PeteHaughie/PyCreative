"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter2/Example_2_1_Forces/Example_2_1_Forces.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 2-1: Forces
"""

from pycreative.app import Sketch
from Mover import Mover


class Example_2_01_Forces(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 2.1: Forces")
        self.mover = Mover(self)
        self.mouse_is_pressed = False
        print("Click mouse to apply wind force.")

    def draw(self):
        self.background(255)

        gravity = self.pvector(0, 0.1)
        self.mover.apply_force(gravity)

        if self.mouse_is_pressed:
            wind = self.pvector(0.1, 0)
            self.mover.apply_force(wind)

        self.mover.update()
        self.mover.display()
        self.mover.check_edges()
    
    def mouse_pressed(self):
        self.mouse_is_pressed = True

    def mouse_released(self):
        self.mouse_is_pressed = False
