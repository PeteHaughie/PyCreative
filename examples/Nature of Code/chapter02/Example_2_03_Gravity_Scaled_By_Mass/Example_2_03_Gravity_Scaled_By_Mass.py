"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter2/Example_2_3_Gravity_Scaled_By_Mass/Example_2_3_Gravity_Scaled_By_Mass.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 2-3: Gravity Scaled by Mass
"""

from Mover import Mover


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 2.3 Gravity Scaled by Mass")
        # A large Mover on the left side of the window
        self.mover_a = Mover(self, 200, 30, 10)
        # A smaller Mover on the right side of the window
        self.mover_b = Mover(self, 440, 30, 2)
        self.mouse_is_pressed = False

    def draw(self):
        self.background(255)

        gravity = self.pcvector(0, 0.1)
        gravity_a = gravity.copy().mult(self.mover_a.mass)
        self.mover_a.apply_force(gravity_a)

        gravity_b = gravity.copy().mult(self.mover_b.mass)
        self.mover_b.apply_force(gravity_b)

        if self.mouse_is_pressed:
            wind = self.pcvector(0.1, 0)
            self.mover_a.apply_force(wind)
            self.mover_b.apply_force(wind)

        self.mover_a.update()
        self.mover_a.show()
        self.mover_a.check_edges()

        self.mover_b.update()
        self.mover_b.show()
        self.mover_b.check_edges()
    
    def mouse_pressed(self):
        self.mouse_is_pressed = True

    def mouse_released(self):
        self.mouse_is_pressed = False
    