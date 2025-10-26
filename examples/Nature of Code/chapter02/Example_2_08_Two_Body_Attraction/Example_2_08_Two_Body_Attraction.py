"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter2/Example_2_8_Two_Body_Attraction/Example_2_8_Two_Body_Attraction.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 2.8: Two Body Attraction
"""

from Body import Body


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("Example 2.8: Two Body Attraction")
        self.bodyA = Body(self, 320, 60)
        self.bodyB = Body(self, 320, 300)
        self.bodyA.velocity = self.pcvector(1, 0)
        self.bodyB.velocity = self.pcvector(-1, 0)

    def draw(self):
        self.background(255)

        self.bodyA.attract(self.bodyB)
        self.bodyB.attract(self.bodyA)

        self.bodyA.update()
        self.bodyA.draw()
        self.bodyB.update()
        self.bodyB.draw()
