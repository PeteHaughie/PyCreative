from pycreative import Sketch


class MySketch(Sketch):
    def setup(self):
        self.size(800, 600)
        self.bg = 0

    def update(self, dt):
        pass  # Update state here

    def draw(self):
        self.clear(self.bg)
        self.ellipse(self.width / 2, self.height / 2, 200, 200)  # Center


if __name__ == "__main__":
    MySketch().run()
