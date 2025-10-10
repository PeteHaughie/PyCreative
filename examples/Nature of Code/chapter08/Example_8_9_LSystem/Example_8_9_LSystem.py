"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter8/Example_8_9_LSystem/Example_8_9_LSystem.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// L-Systems
"""

from pycreative.app import Sketch
from Turtle import Turtle
from LSystem import LSystem


class Example_8_9_LSystem(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 8-9: L-System")
        rules = {'F': "FF+[+F-F-F]-[-F+F+F]"}
        self.lsystem = LSystem("F", rules)
        self.turtle = Turtle(self, 6, self.radians(25))

        for _ in range(4):
            self.lsystem.generate()

        # Some other rules
        # ruleset = {'F': "F[F]-F+F[--F]+F-F"}
        # self.lsystem = LSystem("F-F-F-F", ruleset)
        # self.turtle = Turtle(self, 4, self.PI / 2)

        # ruleset = {'F': "F--F--F--G", 'G': "GG"}
        # self.lsystem = LSystem("F--F--F", ruleset)
        # self.turtle = Turtle(self, 16, self.PI / 3)

    def draw(self):
        self.background(255)
        self.translate(self.width / 2, self.height)
        self.turtle.render(self.lsystem.sentence)
        self.no_loop()
