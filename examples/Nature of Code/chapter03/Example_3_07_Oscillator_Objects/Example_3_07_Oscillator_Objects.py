"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter3/Example_3_7_Oscillator_Objects/Example_3_7_Oscillator_Objects.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 3.7: Oscillator Objects
"""

from Oscillator import Oscillator


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 3.7 Oscillator Objects")
        # Initialize all objects
        self.oscillators = [Oscillator(self) for _ in range(10)]

    def update(self, dt):
        for osc in self.oscillators:
            osc.update()

    def draw(self):
        self.background(255)
        # Run all objects
        for osc in self.oscillators:
            osc.show()
