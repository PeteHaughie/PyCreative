"""
Turtle class for Example 8-9: L-System
"""

class Turtle:
    def __init__(self, sketch, length: int, angle: float):
        self.sketch = sketch
        self.length = length
        self.angle = angle

    def render(self, sentence: str):
        self.sketch.stroke(0)
        for c in sentence:
            if c == 'F' or c == 'G':
                self.sketch.line(0, 0, 0, -self.length)
                self.sketch.translate(0, -self.length)
            elif c == '+':
                self.sketch.rotate(self.angle)
            elif c == '-':
                self.sketch.rotate(-self.angle)
            elif c == '[':
                self.sketch.push()
            elif c == ']':
                self.sketch.pop()
