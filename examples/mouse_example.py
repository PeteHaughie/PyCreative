"""
Minimal mouse example for PyCreative
"""

from pycreative import Sketch

class MouseDemo(Sketch):
    def setup(self):
        self.size(400, 300)
        self.bg = (30, 30, 30)

    def draw(self):
        self.clear(self.bg)
        x, y = self.mouse.pos.x, self.mouse.pos.y
        color = (100, 100, 100)
        if self.mouse.left:
            color = (255, 0, 0)
        elif self.mouse.middle:
            color = (0, 255, 0)
        elif self.mouse.right:
            color = (0, 0, 255)
        self.ellipse(x, y, 40, 40, color)
        # Show a larger ellipse for one frame after button release
        if self.mouse.left_up:
            self.ellipse(x, y, 40, 40, (255, 200, 200))
        if self.mouse.middle_up:
            self.ellipse(x, y, 40, 40, (200, 255, 200))
        if self.mouse.right_up:
            self.ellipse(x, y, 40, 40, (200, 200, 255))

if __name__ == "__main__":
    MouseDemo().run()
