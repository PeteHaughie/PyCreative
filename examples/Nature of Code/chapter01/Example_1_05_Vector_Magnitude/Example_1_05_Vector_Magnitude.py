"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter1/Example_1_5_Vector_Magnitude/Example_1_5_Vector_Magnitude.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 1-5: Vector magnitude
"""


class Sketch:
    def setup(self):
        self.size(640, 360)

    def draw(self):
        self.background(255)

        mouse = self.pcvector(self.mouse_x, self.mouse_y)
        center = self.pcvector(self.width / 2, self.height / 2)
        mouse.sub(center)

        # The magnitude (i.e. length) of a vector can be accessed via the mag() function.
        # Here it is used as the width of a rectangle drawn at the top of the window.
        m = mouse.mag()
        self.fill(0)
        self.rect(10, 10, m, 10)

        self.translate(self.width / 2, self.height / 2)
        self.line(0, 0, mouse.x, mouse.y)
