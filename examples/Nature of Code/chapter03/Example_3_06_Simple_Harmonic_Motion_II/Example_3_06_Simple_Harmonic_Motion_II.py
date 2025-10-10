"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter3/Example_3_6_Simple_Harmonic_Motion_II/Example_3_6_Simple_Harmonic_Motion_II.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 3.6: Simple Harmonic Motion II
"""

from pycreative.app import Sketch


class Example_3_06_Simple_Harmonic_Motion_II(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 3.6: Simple Harmonic Motion II")
        self.angle = 0.0
        self.angle_velocity = 0.05

    def draw(self):
        self.background(255)

        amplitude = 200
        x = amplitude * self.sin(self.angle)
        self.angle += self.angle_velocity

        self.push()
        try:
            self.translate(self.width / 2, self.height / 2)
            self.stroke((0, 0, 0))
            self.stroke_weight(2)
            self.fill(127)
            self.line(0, 0, x, 0)
            self.circle(x, 0, 48)
        finally:
            self.pop()
