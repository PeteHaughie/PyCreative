# A minimal example of a PyCreative sketch

from pycreative.app import Sketch

class MySketch(Sketch):
    def setup(self):
        self.size(800, 600)
        self.background(255)

    def update(self):
        pass

    def draw(self):
        self.fill(0)
        self.circle(self.width // 2, self.height // 2, 100)