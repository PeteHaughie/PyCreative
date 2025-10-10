"""
Path object for Example 5-5: Create Path Object
"""


class Path:
    def __init__(self, sketch):
        self.sketch = sketch
        # A path has a radius, how wide is it.
        # {!3} Picking some arbitrary values to initialize the path
        self.radius = 20
        self.start = sketch.pvector(0, sketch.height / 3)
        # {!2} A path is only two points, start and end.
        self.end = sketch.pvector(sketch.width, (2 * sketch.height) / 3)

    # {!7} Display the path.
    def show(self):
        self.sketch.stroke(0, 100)
        self.sketch.stroke_weight(self.radius * 2)
        self.sketch.line(self.start.x, self.start.y, self.end.x, self.end.y)
        self.sketch.stroke(0)
        self.sketch.stroke_weight(1)
        self.sketch.line(self.start.x, self.start.y, self.end.x, self.end.y)
