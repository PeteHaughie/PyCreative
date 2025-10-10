"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter3/Example_3_4_Polar_To_Cartesian/Example_3_4_Polar_To_Cartesian.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 3.4: Polar to Cartesian
"""

from pycreative.app import Sketch


class Example_3_04_Polar_To_Cartesian(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 3.4: Polar to Cartesian")
        # Initialize all values
        self.r = self.height * 0.35
        self.theta = 0.0

    def draw(self):
        self.background(255)

        # Translate the origin point to the center of the screen
        self.translate(self.width / 2, self.height / 2)

        # Convert polar to cartesian
        x = self.r * self.cos(self.theta)
        y = self.r * self.sin(self.theta)

        # Draw the ellipse at the cartesian coordinate
        self.fill(127)
        self.stroke(0)
        self.stroke_weight(2)
        self.line(0, 0, x, y)
        self.circle(x, y, 48)

        # Increase the angle over time
        self.theta += 0.02
