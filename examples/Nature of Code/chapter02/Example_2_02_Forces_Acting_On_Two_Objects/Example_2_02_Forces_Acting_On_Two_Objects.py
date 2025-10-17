"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter2/Example_2_2_Forces_Acting_On_Two_Objects/Example_2_2_Forces_Acting_On_Two_Objects.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 2-2: Forces Acting on Two Objects
"""

from Mover import Mover


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 2.2 Forces Acting on Two Objects")
        # A large Mover on the left side of the window
        self.mover_a = Mover(self)
        self.mover_a.position = self.pcvector(200, 30)
        self.mover_a.mass = 10
        # A smaller Mover on the right side of the window
        self.mover_b = Mover(self)
        self.mover_b.position = self.pcvector(440, 30)
        self.mover_b.mass = 2
        self.mouse_is_pressed = False
        print("Click mouse to apply wind force.")

    def draw(self):
        self.background(255)

        gravity = self.pcvector(0, 0.1)
        self.mover_a.apply_force(gravity)
        self.mover_b.apply_force(gravity)

        if self.mouse_is_pressed:
            wind = self.pcvector(0.1, 0)
            self.mover_a.apply_force(wind)
            self.mover_b.apply_force(wind)

        self.mover_a.update()
        self.mover_a.draw()
        self.mover_a.check_edges()

        self.mover_b.update()
        self.mover_b.draw()
        self.mover_b.check_edges()

    def mouse_pressed(self):
        self.mouse_is_pressed = True

    def mouse_released(self):
        self.mouse_is_pressed = False
