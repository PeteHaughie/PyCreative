"""
Minimal example sketch for PyCreative.
Runs for 60 frames.
"""
from pycreative import Sketch

class MySketch(Sketch):
    def setup(self):
        self.size(320, 240)
        self.bg = (0, 0, 0)
        print("setup called")
    def draw(self):
        self.clear(self.bg)
        self.ellipse(self.width/2, self.height/2, 100, 100, color=(255, 255, 255))
    def teardown(self):
        print("teardown called")

if __name__ == "__main__":
    MySketch().run()
