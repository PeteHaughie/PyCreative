from pycreative import Sketch

class DiagonalsSketch(Sketch):
    def setup(self):
        self.size(100, 100)

    def update(self, dt):
        pass

    def draw(self):
        self.clear(self.bg)
        self.diagonals(40, 90)
        self.diagonals(60, 62)
        self.diagonals(20, 40)

    def diagonals(self, x, y):
        self.line((x, y), (x + 20, y - 40))
        self.line((x + 10, y), (x + 30, y - 40))
        self.line((x + 20, y), (x + 40, y - 40))

if __name__ == "__main__":
    DiagonalsSketch().run()