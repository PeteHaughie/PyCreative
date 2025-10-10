"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter3/Example_3_7_Oscillator_Objects/Example_3_7_Oscillator_Objects.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 3.7: Oscillator Objects
"""

from pycreative.app import Sketch
from Oscillator import Oscillator


class Example_3_07_Oscillator_Objects(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 3.7: Oscillator Objects")
        # Initialize all objects
        self.oscillators = [Oscillator(self) for _ in range(10)]

    def update(self, dt):
        for osc in self.oscillators:
            osc.update()

    def draw(self):
        self.clear(255)
        # Run all objects
        for osc in self.oscillators:
            osc.draw()
