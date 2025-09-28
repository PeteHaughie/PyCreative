from pycreative import Sketch


class SketchLifecycle(Sketch):
    def setup(self):
        self.size(400, 300)
        self.set_title("Sketch lifecycle")
        self.frame_rate(60)

    def update(self, dt):
        pass

    def draw(self):
        self.clear((30, 30, 30))

    def teardown(self):
        # no-op cleanup for example
        pass


if __name__ == "__main__":
    SketchLifecycle().run()