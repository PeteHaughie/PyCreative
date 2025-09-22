"""
stroke_example.py: Example sketch showing stroke customization in Sketch format.
"""

from pycreative import Sketch

class StrokeExample(Sketch):
    def setup(self):
        self.size(800, 650)
        self.set_title("Stroke Example")
        self.bg = (50, 50, 50)

    def draw(self):
        self.noFill()
        self.clear(self.bg)
        self.stroke(255, 0, 0)
        self.stroke_weight(4)
        self.rect(100, 10, 600, 200)
        self.noStroke()
        self.fill(0, 255, 0)
        self.rect(100, 220, 600, 200)
        self.rect(100, 430, 600, 200, stroke=(0, 0, 255), stroke_width=4, fill=(255, 255, 0))

if __name__ == "__main__":
    StrokeExample().run()