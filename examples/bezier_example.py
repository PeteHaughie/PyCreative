"""
graphics_demo.py: Example sketch using pycreative.graphics.Surface primitives in Sketch format.
"""

from pycreative import Sketch


class BezierDemo(Sketch):
    def setup(self):
        self.size(100, 100)
        self.bg = (0, 0, 0)
        self.stroke(255, 255, 255)
        self.stroke_weight(2)

    def update(self, dt):
        pass

    def draw(self):
        self.clear(self.bg)
        self.bezier(32, 20, 80, 5, 80, 75, 30, 75)
        self.line(32, 20, 80, 5, stroke_width=1)
        self.ellipse(80, 5, 4, 4)
        self.line(80, 75, 30, 75, stroke_width=1)
        self.ellipse(80, 75, 4, 4, stroke_width=1)


if __name__ == "__main__":
    BezierDemo().run()
