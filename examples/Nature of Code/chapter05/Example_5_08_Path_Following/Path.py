"""
Path class for Example 5-8: Path Following
"""

class Path:
    def __init__(self, sketch):
        self.sketch = sketch
        # A path has a radius, i how far is it ok for the vehicle to wander off
        self.radius = 20
        # A Path is an array of points (PVector objects)
        self.points = []

    # Add a point to the path
    def add_point(self, x, y):
        point = self.sketch.pvector(x, y)
        self.points.append(point)

    def get_start(self):
        return self.points[0]

    def get_end(self):
        return self.points[-1]

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
