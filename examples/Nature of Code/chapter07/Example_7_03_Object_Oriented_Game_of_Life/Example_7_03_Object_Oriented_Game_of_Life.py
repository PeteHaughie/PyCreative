"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter7/Example_7_3_Object_Oriented_Game_of_Life/Example_7_3_Object_Oriented_Game_of_Life.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 7-3: Object-Oriented Game of Life
"""

from pycreative.app import Sketch
from Cell import Cell


class Example_7_03_Object_Oriented_Game_of_Life(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 7-3: Object-Oriented Game of Life")
        self.w = 8
        self.columns = self.width // self.w
        self.rows = self.height // self.w
        self.board = self.create2DArray(self.columns, self.rows)
        for i in range(1, self.columns - 1):
            for j in range(1, self.rows - 1):
                from random import randint

                self.board[i][j] = Cell(randint(0, 1), i * self.w, j * self.w, self.w)

    def draw(self):
        # Looping but skipping the edge cells
        for x in range(1, self.columns - 1):
            for y in range(1, self.rows - 1):
                neighborSum = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        # Use the previous state when counting neighbors
                        neighborSum += self.board[x + i][y + j].previous
                neighborSum -= self.board[x][y].previous

                # Set the cell's new state based on the neighbor count
                if self.board[x][y].state == 1 and neighborSum < 2:
                    self.board[x][y].state = 0
                elif self.board[x][y].state == 1 and neighborSum > 3:
                    self.board[x][y].state = 0
                elif self.board[x][y].state == 0 and neighborSum == 3:
                    self.board[x][y].state = 1
                # else do nothing!

        for i in range(self.columns):
            for j in range(self.rows):
                # evaluates to 255 when state is 0 and 0 when state is 1
                self.board[i][j].show(self)

                # save the previous state before the next generation!
                self.board[i][j].previous = self.board[i][j].state

    def create2DArray(self, columns: int, rows: int):
        arr = [[Cell(0, i * self.w, j * self.w, self.w) for j in range(rows)] for i in range(columns)]
        return arr
    
    def key_pressed(self):
        if self.key == 's':
            self.save_frame("Example_7_03_Object_Oriented_Game_of_Life-##.png")
