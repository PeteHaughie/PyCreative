"""
Example sketch for PyGameSynth
"""

from pycreative import Sketch

class MySketch(Sketch):
    def setup(self):
        self.size(400, 300)
        print("Setup complete.")
    def draw(self):
        self.clear((50, 50, 50))
        # Draw a moving ellipse
        x = (self.frame_count * 5) % self.width
        self.ellipse(x, self.height // 2, 50, 50, color=(200, 100, 100))
    def teardown(self):
        print("Teardown complete.")

if __name__ == "__main__":
    MySketch().run()
