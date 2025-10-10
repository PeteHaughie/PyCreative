"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter8/Example_8_6_Recursive_Tree/Example_8_6_Recursive_Tree.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Recursive Tree
// Renders a simple tree-like structure via recursion
// Branching angle calculated as a function of horizontal mouse position
"""

from pycreative.app import Sketch


class Example_8_6_Recursive_Tree(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 8-6: Recursive Tree")

    def draw(self):
        self.background(255)
        # Mapping the angle between 0 to 90° (HALF_PI) according to mouseX
        self.angle = self.map(self.mouse_x or 0, 0, self.width, 0, self.HALF_PI)

        # Start the tree from the bottom of the canvas
        self.translate(self.width / 2, self.height)
        self.stroke(0)
        self.stroke_weight(2)
        self.branch(100)

    # {!1} Each branch now receives its length as an argument.
    def branch(self, length: float):
        self.line(0, 0, 0, -length)
        self.translate(0, -length)

        # {!1} Each branch's length shrinks by two-thirds.
        length *= 0.67

        if length > 2:
            self.push()
            try:
              self.rotate(self.angle)
              # {!1} Subsequent calls to branch() include the length argument.
              self.branch(length)
              self.pop()

              self.push()
              self.rotate(-self.angle)
              self.branch(length)
            finally:
              self.pop()
