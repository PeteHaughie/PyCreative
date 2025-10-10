"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_2_Arrive/Example_5_2_Arrive.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Arriving "vehicle" follows the mouse position

// Implements Craig Reynold's autonomous steering behaviors
// One vehicle "arrive"
// See: http://www.red3d.com/cwr/
"""

from pycreative.app import Sketch
from Vehicle import Vehicle


class Example_5_02_Arrive(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 5.2: Arrive")
        self.vehicle = Vehicle(self, self.width / 2, self.height / 2)

    def update(self, dt):
        self.vehicle.update()

    def draw(self):
        self.background(255)
        mouse = self.pvector(self.mouse_x or 0, self.mouse_y or 0)
    
        # Draw an ellipse at the mouse position
        self.fill(127)
        self.stroke(0)
        self.stroke_weight(2)
        self.circle(mouse.x, mouse.y, 48)

        # Call the appropriate steering behaviors for our agents
        self.vehicle.arrive(mouse)
        self.vehicle.show()

    def mouse_pressed(self):
        self.save_frame("screenshot.png")
