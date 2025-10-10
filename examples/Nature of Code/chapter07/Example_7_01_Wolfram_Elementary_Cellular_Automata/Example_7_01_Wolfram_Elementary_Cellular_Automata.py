"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter7/Example_7_1_Wolfram_Elementary_Cellular_Automata/Example_7_1_Wolfram_Elementary_Cellular_Automata.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 7-1: Wolfram Elementary Cellular Automata
"""

from pycreative.app import Sketch


class Example_7_01_Wolfram_Elementary_Cellular_Automata(Sketch):
    def setup(self):
        self.size(640, 320)
        self.set_title("Example 7-1: Wolfram Elementary Cellular Automata")
        self.background(255)
        # An array of 0s and 1s
        self.cells = [0] * (self.width // self.w)
        self.cells[len(self.cells) // 2] = 1

    def draw(self):
        for i in range(1, len(self.cells) - 1):
            # Only drawing the cell's with a state of 1
            if self.cells[i] == 1:
                self.fill(0)
                # Set the y-position according to the generation.
                self.square(i * self.w, self.generation * self.w, self.w)

        # Compute the next generation.
        nextgen = self.cells[:]
        for i in range(1, len(self.cells) - 1):
            left = self.cells[i - 1]
            me = self.cells[i]
            right = self.cells[i + 1]
            nextgen[i] = self.rules(left, me, right)
        self.cells = nextgen

        # The next generation
        self.generation += 1

        # Stopping when it gets to the bottom of the canvas
        if self.generation * self.w > self.height:
            self.no_loop()

    # Look up a new state from the ruleset.
    def rules(self, a, b, c):
        s = f"{a}{b}{c}"
        index = int(s, 2)
        return self.ruleset[7 - index]
    
    def key_pressed(self):
        if self.key == 's':
            self.save_frame("Example_7_01_Wolfram_Elementary_Cellular_Automata-##.png")

    # Array of cells
    cells = []
    # Starting at generation 0
    generation = 0
    # Cell size
    w = 10

    # Rule 90
    ruleset = [0, 1, 0, 1, 1, 0, 1, 0]
