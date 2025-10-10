"""
Flow Field class for Example 5-4: Flow Field
"""


class FlowField:
    def __init__(self, sketch, resolution: int):
        self.sketch = sketch
        self.resolution = resolution
        self.cols = 0
        self.rows = 0
        self.field: list[list[self.sketch.pvector]] = []
        self.init_dimensions()

    def init(self):
        self.init_dimensions()

    def init_dimensions(self):
        self.cols = self.sketch.width // self.resolution
        self.rows = self.sketch.height // self.resolution
        self.field = [[self.sketch.pvector(0, 0) for _ in range(self.rows)] for _ in range(self.cols)]
        self.init_field()

    def init_field(self):
        for i in range(self.cols):
            for j in range(self.rows):
                self.field[i][j] = self.sketch.pvector(0, 0)
        noise_seed = self.sketch.random(0, 10000)
        self.sketch.noise_seed(noise_seed)
        xoff = 0.0
        for i in range(self.cols):
            yoff = 0.0
            for j in range(self.rows):
                angle = self.sketch.map(self.sketch.noise(xoff, yoff), 0, 1, 0, self.sketch.TWO_PI)
                self.field[i][j] = self.sketch.pvector.from_angle(angle)
                yoff += 0.1
            xoff += 0.1

    def show(self, debug):
        if not debug:
            return
        for i in range(self.cols):
            for j in range(self.rows):
                w = self.sketch.width / self.cols
                h = self.sketch.height / self.rows
                v = self.field[i][j].copy()
                v.set_mag(w * 0.5)
                x = i * w + w / 2
                y = j * h + h / 2
                self.sketch.stroke_weight(1)
                self.sketch.line(x, y, x + v.x, y + v.y)
    
    def lookup(self, position):
        column = self.sketch.constrain(int(position.x // self.resolution), 0, self.cols - 1)
        row = self.sketch.constrain(int(position.y // self.resolution), 0, self.rows - 1)
        return self.field[column][row].copy()
