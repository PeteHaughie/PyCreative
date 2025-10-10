"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter0/Example_0_5_Accept_Reject_Distribution/Example_0_5_Accept_Reject_Distribution.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 0-5: Accept-Reject Distribution
"""

from pycreative.app import Sketch


class Example_0_5_Accept_Reject_Distribution(Sketch):
    def setup(self) -> None:
        self.size(640, 360)
        self.total = 20
        self.random_counts = [0] * self.total

    def draw(self) -> None:
        self.background(255)
        index = int(self.accept_reject() * len(self.random_counts))
        self.random_counts[index] += 1

        # Draw a rectangle to graph results
        self.stroke(0)
        self.stroke_weight(2)
        self.fill(127)
        w = self.width / len(self.random_counts)

        for x in range(len(self.random_counts)):
            rc = self.random_counts[x]
            self.rect(x * w, self.height - rc, w - 1, rc)

    def accept_reject(self) -> float:
        # An algorithm for picking a random number based on monte carlo method
        # Here probability is determined by formula y = x
        while True:
            # Pick a random value.
            r1 = self.random(1)
            # Assign a probability.
            probability = r1
            # Pick a second random value.
            r2 = self.random(1)

            # Does it qualify?  If so, we’re done!
            if r2 < probability:
                return r1
