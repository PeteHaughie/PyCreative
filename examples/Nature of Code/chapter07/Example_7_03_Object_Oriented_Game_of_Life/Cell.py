"""
Cell class for Example 7.3: Object Oriented Game of Life
"""

class Cell:
    def __init__(self, sketch, state: int, x: int, y: int, w: int):
        self.sketch = sketch
        # Cell State -> 1 = Alive, 0 = Not Alive
        self.state = state
        self.previous = self.state

        # position and size
        self.x = x
        self.y = y
        self.w = w

    def show(self):
        self.sketch.stroke(0)
        # If the cell is born, color it blue!
        if self.previous == 0 and self.state == 1:
            self.sketch.fill(0, 0, 255)
        elif self.state == 1:
            self.sketch.fill(0)
            # If the cell dies, color it red!
        elif self.previous == 1 and self.state == 0:
            self.sketch.fill(255, 0, 0)
        else:
            self.sketch.fill(255)
        self.sketch.square(self.x, self.y, self.w)
