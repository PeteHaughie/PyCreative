""""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter1/Example_1_6_Vector_Normalize/Example_1_6_Vector_Normalize.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 1-6: Vector normalize
"""

from pycreative.app import Sketch


class Example_1_6_Vector_Normalize(Sketch):
    def setup(self):
        self.size(640, 360)

    def draw(self):
        self.background(255)

        mouse = self.pvector(self.mouse_x, self.mouse_y)
        center = self.pvector(self.width / 2, self.height / 2)
        mouse.sub(center)

        self.translate(self.width / 2, self.height / 2)
        self.stroke(200)
        self.stroke_weight(2)
        self.line(0, 0, mouse.x, mouse.y)

        # Normalize the vector
        mouse.normalize()

        # Multiply its length by 50
        mouse.mult(50)

        # Draw the resulting vector
        self.stroke(0)
        self.stroke_weight(8)
        self.line(0, 0, mouse.x, mouse.y)
