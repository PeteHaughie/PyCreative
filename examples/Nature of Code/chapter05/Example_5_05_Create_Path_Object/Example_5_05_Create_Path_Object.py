"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_5_Create_Path_Object/Example_5_5_Create_Path_Object.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Path Following
// Path is a just a straight line in this example
// Via Reynolds: // http://www.red3d.com/cwr/steer/PathFollow.html

// A path object (series of connected points)
"""

from pycreative.app import Sketch
from Path import Path


class Example_5_05_Create_Path_Object(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 5.5: Create Path Object")
        self.path = Path(self)

    def draw(self):
        self.background(255)
        self.path.show()
