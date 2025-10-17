"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter1/Example_1_3_Vector_Subtraction/Example_1_3_Vector_Subtraction.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 1-3: Vector subtraction
"""


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 1-3 Vector Subtraction")

    def draw(self):
        self.background(255)
        mouse = self.pcvector(self.mouse_x, self.mouse_y)
        center = self.pcvector(self.width // 2, self.height // 2)

        self.stroke_weight(4)
        self.stroke(200)
        self.line(0, 0, mouse.x, mouse.y)
        self.line(0, 0, center.x, center.y)
        
        mouse.sub(center)
        self.stroke(0)
        self.translate(self.width / 2, self.height / 2)
        self.line(0, 0, mouse.x, mouse.y)
