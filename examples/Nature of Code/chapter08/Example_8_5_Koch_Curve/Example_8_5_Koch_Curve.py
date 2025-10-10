"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter8/Example_8_5_Koch_Curve/Example_8_5_Koch_Curve.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Koch Curve
// Renders a simple fractal, the Koch snowflake
// Each recursive level drawn in sequence
"""

from pycreative.app import Sketch
from KochLine import KochLine


class Example_8_5_Koch_Curve(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 8-5: Koch Curve")
        # An array for all the line segments
        self.segments = []

        # Left side of canvas
        start = self.pvector(0, 300)
        # Right side of canvas
        end = self.pvector(self.width, 300)

        # The first KochLine object
        self.segments.append(KochLine(self, start, end))

        # Apply the Koch rules five times.
        for _ in range(5):
            self.generate()

        self.no_loop()

    def draw(self):
        self.background(255)
        for segment in self.segments:
            segment.show()
        self.no_loop()

    def generate(self):
        # Create the next array
        next_segments = []
        # For every segment
        for segment in self.segments:
            # Calculate 5 koch PVectors (done for us by the line object)
            koch_points = segment.koch_points()
            a = koch_points[0]
            b = koch_points[1]
            c = koch_points[2]
            d = koch_points[3]
            e = koch_points[4]
            # Make line segments between all the vectors and add them
            next_segments.append(KochLine(self, a, b))
            next_segments.append(KochLine(self, b, c))
            next_segments.append(KochLine(self, c, d))
            next_segments.append(KochLine(self, d, e))
        # The next segments!
        self.segments = next_segments
