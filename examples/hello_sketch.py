"""
Minimal example sketch for PyCreative.
Runs headless for 3 frames.
"""
from pycreative import Sketch

class MySketch(Sketch):
    def setup(self):
        self.size(320, 240)
        self.bg = (0, 0, 0)
    def draw(self):
        self.clear(self.bg)
        self.ellipse(self.width/2, self.height/2, 100, 100, color=(255, 255, 255))

if __name__ == "__main__":
    MySketch().run(max_frames=3)
