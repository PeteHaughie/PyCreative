"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter1/Example_1_2_Bouncing_Ball_Vectors/Example_1_2_Bouncing_Ball_Vectors.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 1-2: Bouncing Ball, with PVector!
"""


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 1-2 Bouncing Ball Vectors")
        self.position = self.pcvector(100, 100)
        self.velocity = self.pcvector(2.5, 2)

    def draw(self):
        self.background(255)
        self.position.add(self.velocity)

        if self.position.x > self.width or self.position.x < 0:
            self.velocity.x = self.velocity.x * -1
        if self.position.y > self.height or self.position.y < 0:
            self.velocity.y = self.velocity.y * -1

        self.stroke(0)
        self.fill(127)
        self.stroke_weight(2)
        self.circle(self.position.x, self.position.y, 48)
