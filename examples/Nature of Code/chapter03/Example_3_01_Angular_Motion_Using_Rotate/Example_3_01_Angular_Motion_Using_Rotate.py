"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter3/Example_3_1_Angular_Motion_Using_Rotate/Example_3_1_Angular_Motion_Using_Rotate.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 3.1: Angular Motion Using Rotate
"""

from pycreative.app import Sketch


class Example_3_01_Angular_Motion_Using_Rotate(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 3.1: Angular Motion Using Rotate")
        # Position
        self.angle = 0.0
        # Velocity
        self.angle_velocity = 0.0
        # Acceleration
        self.angle_acceleration = 0.0001

    def update(self, dt):
        pass

    def draw(self):
        self.clear(255)

        self.translate(self.width / 2, self.height / 2)
        self.rotate(self.angle)

        self.stroke(0)
        self.stroke_weight(2)
        self.fill(127)

        self.line(-60, 0, 60, 0)
        self.circle(60, 0, 16)
        self.circle(-60, 0, 16)

        # Angular equivalent of velocity.add(acceleration);
        self.angle_velocity += self.angle_acceleration
        # Angular equivalent of position.add(velocity);
        self.angle += self.angle_velocity
