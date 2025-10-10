"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter0/Example_0_2_Random_Distribution/Example_0_2_Random_Distribution.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 0-2: Random Distribution
"""

from pycreative.app import Sketch

class Example_0_2_Random_Distribution(Sketch):
    def setup(self) -> None:
        self.size(640, 360)
        self.total = 20
        self.random_counts = [0] * self.total

    def draw(self) -> None:
        self.background(255)
        index = int(self.random(self.total))
        self.random_counts[index] += 1

        # Draw a rectangle to graph results
        self.stroke(0)
        self.stroke_weight(2)
        self.fill(127)
        w = self.width / len(self.random_counts)

        for x in range(len(self.random_counts)):
            rc = self.random_counts[x]
            self.rect(x * w, self.height - rc, w - 1, rc)
