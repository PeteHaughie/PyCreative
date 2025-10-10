"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_8_Path_Following/Example_5_8_Path_Following.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Path Following
// Path is a just a straight line in this example
// Via Reynolds: // http://www.red3d.com/cwr/steer/PathFollow.html

// A path is a series of connected points
"""

from pycreative.app import Sketch
from Path import Path
from Vehicle import Vehicle


class Example_5_8_Path_Following(Sketch):
    def setup(self):
        self.size(640, 360)
        print("Hit space bar to toggle debugging lines.\nClick the mouse to generate a new path.")

        self.new_path()

        # Each vehicle has different maxspeed and maxforce for demo purposes
        self.car1 = Vehicle(self, 0, self.height / 2, 2, 0.04)
        self.car2 = Vehicle(self, 0, self.height / 2, 3, 0.1)

        self.debug = True

    def draw(self):
        self.background((255, 255, 255))
        # Display the path
        self.path.show()
        # The boids follow the path
        self.car1.follow(self.path)
        self.car2.follow(self.path)
        # Call the generic run method (update, borders, display, etc.)
        self.car1.run()
        self.car2.run()

        # Check if it gets to the end of the path since it's not a loop
        self.car1.borders(self.path)
        self.car2.borders(self.path)

    def new_path(self):
        # A path is a series of connected points
        # A more sophisticated path might be a curve
        self.path = Path(self)
        self.path.add_point(-20, self.height / 2)
        from random import uniform

        self.path.add_point(uniform(0, self.width / 2), uniform(0, self.height))
        self.path.add_point(uniform(self.width / 2, self.width), uniform(0, self.height))
        self.path.add_point(self.width + 20, self.height / 2)

    def key_pressed(self):
        if self.key == ' ':
            self.debug = not self.debug

    def mouse_pressed(self):
        self.new_path()
