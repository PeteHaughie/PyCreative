"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_6_Simple_Path_Following/Example_5_6_Simple_Path_Following.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Path Following
// Path is a just a straight line in this example
// Via Reynolds: // http://www.red3d.com/cwr/steer/PathFollow.html
"""

from pycreative.app import Sketch
from Vehicle import Vehicle
from Path import Path


class Example_5_6_Simple_Path_Following(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 5.6: Simple Path Following")
        self.debug = True  # Using this variable to decide whether to draw all the stuff
        self.path = Path(self)  # A path object (series of connected points)
        # Two vehicles
        # Each vehicle has different maxspeed and maxforce for demo purposes
        self.vehicle1 = Vehicle(self, 0, self.height / 2, 2, 0.02)
        self.vehicle2 = Vehicle(self, 0, self.height / 2, 3, 0.05)

    def update(self, dt):
        pass

    def draw(self):
        self.background((255, 255, 255))
        # Display the path
        self.path.show()
        # The boids follow the path
        self.vehicle1.follow(self.path)
        self.vehicle2.follow(self.path)
        # Call the generic run method (update, borders, display, etc.)
        self.vehicle1.run()
        self.vehicle2.run()

        # Check if it gets to the end of the path since it's not a loop
        self.vehicle1.borders(self.path)
        self.vehicle2.borders(self.path)

    def key_pressed(self):
        if self.key == ' ':
            self.debug = not self.debug