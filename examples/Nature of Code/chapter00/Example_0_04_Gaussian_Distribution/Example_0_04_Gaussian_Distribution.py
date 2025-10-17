"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter0/Example_0_4_Gaussian_Distribution/Example_0_4_Gaussian_Distribution.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 0-4: Gaussian Distribution
"""

class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 0-4 Gaussian Distribution")
        self.background(255)

    def draw(self):
        # A normal distribution with mean 320 and standard deviation 60
        x = self.random_gaussian() * 60 + 320
        self.no_stroke()
        self.fill(0, 10)
        self.circle(x, 120, 16)
