"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_7_Multiple_Segments/Example_5_7_Multiple_Segments.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Path Following
// Path is a just a straight line in this example
// Via Reynolds: // http://www.red3d.com/cwr/steer/PathFollow.html
"""

from pycreative.app import Sketch
from Path import Path


class Example_5_7_Multiple_Segments(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 5.7: Multiple Segments")
        self.path = Path(self)
        self.path.add_point(-20, self.height / 2)
        self.path.add_point(100, 50)
        self.path.add_point(400, 200)
        self.path.add_point(self.width + 20, self.height / 2)

    def draw(self):
        self.background(255)
        # Display the path
        self.path.show()
