"""
Path class for Example 5-7: Multiple Segments
"""


class Path:
    def __init__(self, sketch):
        self.sketch = sketch
        self.radius = 20
        # create empty list that will store PVector objects
        self.points = []

    # Add a point to the path
    def add_point(self, x, y):
        point = self.sketch.pvector(x, y)
        self.points.append(point)

    # Draw the path
    def show(self):
        # Draw thick line for radius
        self.sketch.stroke(200)
        self.sketch.stroke_weight(self.radius * 2)
        self.sketch.no_fill()
        self.sketch.begin_shape()
        for path_point in self.points:
            self.sketch.vertex(path_point.x, path_point.y)
        self.sketch.end_shape()
        # Draw thin line for center of path
        self.sketch.stroke(0)
        self.sketch.stroke_weight(1)
        self.sketch.no_fill()
        self.sketch.begin_shape()
        for path_point in self.points:
            self.sketch.vertex(path_point.x, path_point.y)
        self.sketch.end_shape()
