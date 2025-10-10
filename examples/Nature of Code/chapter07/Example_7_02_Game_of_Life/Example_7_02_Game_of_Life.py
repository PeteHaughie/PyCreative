"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter7/Example_7_2_Game_of_Life/Example_7_2_Game_of_Life.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 7-2: Game of Life
"""

from pycreative.app import Sketch


class Example_7_02_Game_of_Life(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 7-2: Game of Life")
        self.w = 8
        self.columns = self.width // self.w
        self.rows = self.height // self.w
        self.board = self.create2DArray(self.columns, self.rows)
        for i in range(1, self.columns - 1):
            for j in range(1, self.rows - 1):
                self.board[i][j] = int(self.random(2))

    def draw(self):
        next_board = self.create2DArray(self.columns, self.rows)

        for i in range(1, self.columns - 1):
            for j in range(1, self.rows - 1):
                neighbor_sum = 0
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        neighbor_sum += self.board[i + dx][j + dy]
                neighbor_sum -= self.board[i][j]

                if self.board[i][j] == 1 and neighbor_sum < 2:
                    next_board[i][j] = 0
                elif self.board[i][j] == 1 and neighbor_sum > 3:
                    next_board[i][j] = 0
                elif self.board[i][j] == 0 and neighbor_sum == 3:
                    next_board[i][j] = 1
                else:
                    next_board[i][j] = self.board[i][j]

        for i in range(self.columns):
            for j in range(self.rows):
                fill_value = 255 - self.board[i][j] * 255
                self.fill(fill_value)
                self.stroke(0)
                self.square(i * self.w, j * self.w, self.w)

        self.board = next_board

    def create2DArray(self, columns: int, rows: int) -> list[list[int]]:
        return [[0 for _ in range(rows)] for _ in range(columns)]
