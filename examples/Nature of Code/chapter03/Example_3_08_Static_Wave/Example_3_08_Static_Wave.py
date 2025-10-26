"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter3/Example_3_8_Static_Wave/Example_3_8_Static_Wave.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 3.8: Static Wave
"""


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("Noc: Example 3.8 Static Wave")

    def draw(self):
        self.background(255)

        angle = 0
        angle_velocity = 0.2
        amplitude = 100

        self.stroke((0, 0, 0))
        self.stroke_weight(2)
        self.fill(127)

        for x in range(0, self.width + 1, 24):
            # 1) Calculate the y position according to amplitude and sine of the angle.
            y = amplitude * self.sin(angle)
            # 2) Draw a circle at the (x,y) position.
            self.circle(x, y + self.height / 2, 48)
            # 3) Increment the angle according to angular velocity.
            angle += angle_velocity
