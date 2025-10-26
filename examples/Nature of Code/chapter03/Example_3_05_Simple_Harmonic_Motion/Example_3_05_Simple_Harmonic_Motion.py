"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter3/Example_3_5_Simple_Harmonic_Motion/Example_3_5_Simple_Harmonic_Motion.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 3.5: Simple Harmonic Motion
"""


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example 3.5 Simple Harmonic Motion")

    def draw(self):
        self.background(255)

        period = 120
        amplitude = 200

        # Calculating horizontal position according to formula for simple harmonic motion
        x = amplitude * self.sin((self.TWO_PI * (self.frame_count or 0)) / period)

        self.stroke(0)
        self.stroke_weight(2)
        self.fill(127)
        self.push_matrix()
        self.translate(self.width / 2, self.height / 2)
        self.line(0, 0, x, 0)
        self.circle(x, 0, 48)
        self.pop_matrix()
