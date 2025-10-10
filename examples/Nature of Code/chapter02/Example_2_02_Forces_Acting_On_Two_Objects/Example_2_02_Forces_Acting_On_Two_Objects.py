"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter2/Example_2_2_Forces_Acting_On_Two_Objects/Example_2_2_Forces_Acting_On_Two_Objects.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 2-2: Forces Acting on Two Objects
"""

from pycreative.app import Sketch
from Mover import Mover


class Example_2_02_Forces_Acting_On_Two_Objects(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 2.2: Forces Acting on Two Objects")
        # A large Mover on the left side of the window
        self.moverA = Mover(self)
        self.moverA.position = self.pvector(200, 30)
        self.moverA.mass = 10
        # A smaller Mover on the right side of the window
        self.moverB = Mover(self)
        self.moverB.position = self.pvector(440, 30)
        self.moverB.mass = 2
        self.mouse_is_pressed = False
        print("Click mouse to apply wind force.")

    def draw(self):
        self.background(255)

        gravity = self.pvector(0, 0.1)
        self.moverA.apply_force(gravity)
        self.moverB.apply_force(gravity)

        if self.mouse_is_pressed:
            wind = self.pvector(0.1, 0)
            self.moverA.apply_force(wind)
            self.moverB.apply_force(wind)

        self.moverA.update()
        self.moverA.draw()
        self.moverA.check_edges()

        self.moverB.update()
        self.moverB.draw()
        self.moverB.check_edges()

    def mouse_pressed(self):
        self.mouse_is_pressed = True

    def mouse_released(self):
        self.mouse_is_pressed = False
