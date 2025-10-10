"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter8/Example_8_7_Stochastic_Tree/Example_8_7_Stochastic_Tree.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Stochastic Tree
// Renders a simple tree-like structure via recursion
// Angles and number of branches are random
"""

from pycreative.app import Sketch


class Example_8_7_Stochastic_Tree(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 8-7: Stochastic Tree")
        self.frame_rate(1)

    def draw(self):
        self.background(255)

        self.stroke(0)
        self.push()
        try:
          # Start the tree from the bottom of the screen
          self.translate(int(self.width / 2), self.height)
          self.stroke_weight(2)
          # Start the recursive branching!
          self.branch(100)
        finally:
          self.pop()

    def branch(self, length: float):
        # Draw the actual branch
        self.line(0, 0, 0, -length)
        # Move along to end
        self.translate(0, -length)

        # Each branch will be 2/3rds the size of the previous one
        length *= 0.67

        # All recursive functions must have an exit condition!!!!
        # Here, ours is when the length of the branch is 2 pixels or less
        if length > 2:
            # A random number of branches
            n = int(self.floor(self.random(1, 4)))
            for i in range(n):
                # Picking a random angle
                angle = self.random(-self.PI / 2, self.PI / 2)
                self.push()  # Save the current state of transformation (i.e. where are we now)
                try:
                    self.rotate(angle)  # Rotate by theta
                    self.branch(length)  # Ok, now call myself to branch again
                finally:
                    self.pop()  # Whenever we get back here, we "pop" in order to restore the previous matrix state
