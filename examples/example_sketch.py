"""
Example sketch for PyCreative
"""

from pycreative import Sketch


class MySketch(Sketch):
    def setup(self):
        self.size(400, 300)
        self.set_title("Example Sketch")
        self.frame_rate(60)
        self.x = 0.0
        self.speed = 120.0  # pixels per second

    def update(self, dt):
        # Move ellipse smoothly using delta time
        self.x += self.speed * dt
        if self.x > self.width:
            self.x = 0.0

    def draw(self):
        self.clear((50, 50, 50))
        self.ellipse(self.x, self.height / 2, 50, 50, fill=(200, 100, 100))

    def teardown(self):
        pass


if __name__ == "__main__":
    MySketch().run()
