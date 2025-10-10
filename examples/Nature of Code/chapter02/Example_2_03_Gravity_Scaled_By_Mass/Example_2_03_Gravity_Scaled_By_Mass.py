"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter2/Example_2_3_Gravity_Scaled_By_Mass/Example_2_3_Gravity_Scaled_By_Mass.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 2-3: Gravity Scaled by Mass
"""

from pycreative.app import Sketch
from Mover import Mover


class Example_2_03_Gravity_Scaled_By_Mass(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 2.3: Gravity Scaled by Mass")
        # A large Mover on the left side of the window
        self.moverA = Mover(self, 200, 30, 10)
        # A smaller Mover on the right side of the window
        self.moverB = Mover(self, 440, 30, 2)
        self.mouse_is_pressed = False

    def draw(self):
        self.background(255)

        gravity = self.pvector(0, 0.1)

        gravityA = gravity.copy().mult(self.moverA.mass)
        self.moverA.apply_force(gravityA)

        gravityB = gravity.copy().mult(self.moverB.mass)
        self.moverB.apply_force(gravityB)

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
    