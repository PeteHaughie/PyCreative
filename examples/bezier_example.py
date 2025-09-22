"""
graphics_demo.py: Example sketch using pycreative.graphics.Surface primitives in Sketch format.
"""

from pycreative import Sketch


class BezierDemo(Sketch):
    def setup(self):
        self.size(100, 100)
        self.bg = (30, 30, 30)

    def update(self, dt):
        pass

    def draw(self):
        self.clear(self.bg)
        self.bezier(32, 20, 80, 5, 80, 75, 30, 75)
        self.line(32, 20, 80, 5)
        self.ellipse(80, 5, 4, 4)
        self.line(80, 75, 30, 75)
        self.ellipse(80, 75, 4, 4)


if __name__ == "__main__":
    BezierDemo().run()
