"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter0/Example_0_3_Random_Walk_Tends_To_Right/Example_0_3_Random_Walk_Tends_To_Right.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 0-3: Random Walk Tends to Right
"""

class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 0-3 Random Walk Tends To Right")
        self.background(255)
        self.walker = Walker(self, int(self.width // 2), int(self.height // 2))

    def draw(self):
        self.walker.update()
        self.walker.draw()

class Walker():
    def __init__(self, sketch, x=0, y=0):
        self.sketch = sketch
        self.x = x
        self.y = y

    def update(self):
        r = self.sketch.random()
        # A 40% of moving to the right!
        if r < 0.4:
            self.x += 1
        elif r < 0.6:
            self.x -= 1
        elif r < 0.8:
            self.y += 1
        else:
            self.y -= 1
        self.x = self.sketch.constrain(self.x, 0, self.sketch.width - 1)
        self.y = self.sketch.constrain(self.y, 0, self.sketch.height - 1)

    def draw(self):
        self.sketch.stroke(0)
        self.sketch.point(self.x, self.y)
