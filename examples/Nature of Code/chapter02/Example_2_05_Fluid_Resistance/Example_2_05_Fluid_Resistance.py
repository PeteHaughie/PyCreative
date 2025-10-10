"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter2/Example_2_5_Fluid_Resistance/Example_2_5_Fluid_Resistance.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Forces (Gravity and Fluid Resistence) with Vectors
"""

from pycreative.app import Sketch
from Mover import Mover
from Liquid import Liquid


class Example_2_05_Fluid_Resistance(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 2.5: Fluid Resistance")
        self.reset() # Create movers
        self.liquid = Liquid(self, 0, self.height / 2, self.width, self.height / 2, 0.1)

    def draw(self):
        self.background(255)
        self.liquid.draw()

        for mover in self.movers:
            if self.liquid.contains(mover):
                drag_force = self.liquid.calculate_drag(mover)
                mover.apply_force(drag_force)

            gravity = self.pvector(0, 0.1 * mover.mass)
            mover.apply_force(gravity)

            mover.update()
            mover.draw()
            mover.check_edges()

    def mouse_pressed(self):
        self.reset()

    def reset(self):
        self.movers = [Mover(self, 40 + i * 70, 0, self.random(0.5, 3)) for i in range(9)]
