"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter3/Example_3_9_The_Wave/Example_3_9_The_Wave.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 3.9: The Wave
"""

from pycreative.app import Sketch


class Example_3_09_The_Wave(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 3.9: The Wave")
        self.start_angle = 0
        self.angle_velocity = 0.2

    def update(self, dt):
        pass

    def draw(self):
        self.clear(255)

        angle = self.start_angle
        self.start_angle += 0.02

        self.stroke(0)
        self.stroke_weight(2)
        self.fill(127, 127)

        for x in range(0, self.width + 1, 24):
            y = self.map(self.sin(angle), -1, 1, 0, self.height)
            self.circle(x, y, 48)
            angle += self.angle_velocity
