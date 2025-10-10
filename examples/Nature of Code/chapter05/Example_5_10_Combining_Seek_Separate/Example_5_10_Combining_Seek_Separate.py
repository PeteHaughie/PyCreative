"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter5/Example_5_10_Combining_Seek_Separate/Example_5_10_Combining_Seek_Separate.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Separation
// Via Reynolds: http://www.red3d.com/cwr/steer/
"""

from pycreative.app import Sketch
from Vehicle import Vehicle


class Example_5_10_Combining_Seek_Separate(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 5.10: Combining Seek and Separate")
        self.vehicles = [Vehicle(self, (int)(self.random(self.width)), (int)(self.random(self.height))) for _ in range(50)]

    def update(self, dt: float = 0) -> None:
        for v in self.vehicles:
            v.apply_behaviors(self.vehicles)
            v.update()
            v.borders()

    def draw(self):
        self.background((255, 255, 255))
        for v in self.vehicles:
            v.apply_behaviors(self.vehicles)
            v.borders()
            v.update()
            v.show()
