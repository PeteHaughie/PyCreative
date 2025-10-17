"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter1/Example_1_1_Bouncing_Ball_No_Vectors/Example_1_1_Bouncing_Ball_No_Vectors.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 1-1: Bouncing Ball, no PVector!
"""


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 1-1 Bouncing Ball No Vectors")
        self.x = 100
        self.y = 100
        self.xspeed = 2.5
        self.yspeed = 2

    def draw(self):
        self.background(255)

        # Move the ball according to its speed.
        self.x = self.x + self.xspeed
        self.y = self.y + self.yspeed

        # Check for bouncing.
        if self.x > self.width or self.x < 0:
            self.xspeed = self.xspeed * -1
        if self.y > self.height or self.y < 0:
            self.yspeed = self.yspeed * -1

        self.stroke(0)
        self.fill(127)
        self.stroke_weight(2)
        # Draw the ball at the position (x,y).
        self.circle(self.x, self.y, 48)
