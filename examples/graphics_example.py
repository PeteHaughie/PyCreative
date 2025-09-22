"""
graphics_demo.py: Example sketch using pycreative.graphics.Surface primitives in Sketch format.
"""

from pycreative import Sketch


class GraphicsDemo(Sketch):
    def setup(self):
        self.size(640, 480)
        self.bg = (30, 30, 30)
        self.frame_rate(60)
        self.center = (self.width // 2, self.height // 2)
        self.radius = 150
        self.speed = 1.0  # radians per second
        self.angle = 0.0  # initial angle

    def update(self, dt):
        self.angle += self.speed * dt  # advance angle by speed * dt
        self.x = self.center[0] + self.radius * self.math.sin(self.angle)
        self.y = self.center[1] + self.radius * self.math.sin(
            self.angle + self.math.pi / 2
        )

    def draw(self):
        self.clear(self.bg)
        self.rect(50, 50, 200, 100, color=(255, 0, 0))
        self.rect(50, 50, 200, 100, color=(255, 0, 0), width=5)
        self.ellipse(320, 240, 120, 80, color=(0, 255, 0))
        self.ellipse(420, 240, 60, 80, color=(0, 255, 0), width=3)
        self.line(self.center, (self.x, self.y), color=(255, 255, 0), width=3)
        self.triangle(60, 10, 25, 60, 75, 65, color=(0, 0, 255))
        self.quad(300, 10, 250, 80, 350, 80, 400, 10, color=(255, 0, 255))


if __name__ == "__main__":
    GraphicsDemo().run()
