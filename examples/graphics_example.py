"""
graphics_demo.py: Example sketch using pycreative.graphics.Surface primitives in Sketch format.
"""

from pycreative import Sketch


class GraphicsDemo(Sketch):
    def setup(self):
        self.size(640, 480)
        self.center = (self.width // 2, self.height // 2)
        self.radius = 150
        self.bg = (30, 30, 30)

    def draw(self):
        self.clear(self.bg)
        self.rect(50, 50, 200, 100, color=(255, 0, 0))
        self.rect(50, 50, 200, 100, color=(255, 0, 0), width=5)
        self.ellipse(320, 240, 120, 80, color=(0, 255, 0))
        self.ellipse(420, 240, 60, 80, color=(0, 255, 0), width=3)
        # Draw a line - parameters: start xy, end xy, color rgb, width px
        t = self.t
        x = self.center[0] + self.radius * self.math.sin(t)
        y = self.center[1] + self.radius * self.math.sin(
            t + self.math.pi / 2
        )  # phase shift for variety
        self.line(self.center, (x, y), color=(255, 255, 0), width=3)


if __name__ == "__main__":
    GraphicsDemo().run()
