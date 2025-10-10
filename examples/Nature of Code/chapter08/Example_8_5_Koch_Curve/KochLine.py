"""
KochLine class for Example 8-5: Koch Curve
"""

from pycreative.vector import PVector


class KochLine:
    def __init__(self, sketch, a: PVector, b: PVector):
        self.sketch = sketch
        self.start = a.copy()
        self.end = b.copy()

    def show(self):
        self.sketch.stroke(0)
        self.sketch.stroke_weight(2)
        self.sketch.line(self.start.x, self.start.y, self.end.x, self.end.y)

    def koch_points(self):
        # Just the first point!
        a = PVector(self.start.x, self.start.y)
        # Just the last point!
        e = PVector(self.end.x, self.end.y)

        # A vector pointing in the direction, 1/3rd the length
        v = self.end - self.start
        v *= 1 / 3.0

        # b is just 1/3 of the way
        b = a + v
        # d is just another 1/3 of the way
        d = b + v

        # Rotate by -PI/3 radians (negative angle so it rotates "up").
        v = v.rotate(-self.sketch.PI / 3)
        # Move along
        c = b + v

        # Return all five points in an array
        points = [a, b, c, d, e]
        return points