"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter1/Example_1_4_Vector_Multiplication/Example_1_4_Vector_Multiplication.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 1-4: Vector Multiplication
"""

from pycreative.app import Sketch


class Example_1_4_Vector_Multiplication(Sketch):
    def setup(self):
        self.size(640, 360)

    def draw(self):
        self.background(255)

        mouse = self.pvector(self.mouse_x, self.mouse_y)
        center = self.pvector(self.width / 2, self.height / 2)
        mouse.sub(center)

        self.translate(self.width / 2, self.height / 2)
        self.stroke_weight(2)
        self.stroke(200)
        self.line(0, 0, mouse.x, mouse.y)

        # Multiplying a vector!  The vector is now half its original size (multiplied by 0.5).
        mouse.mult(0.5)

        self.stroke(0)
        self.stroke_weight(4)
        self.line(0, 0, mouse.x, mouse.y)
