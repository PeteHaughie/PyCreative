from pycreative.app import Sketch


class SaveFrameExample(Sketch):
    def setup(self):
        self.size(640, 480)
        self.set_title("Save Snapshot Example")
        self.set_save_folder("snapshots")
        self.fill((255, 0, 0))

    def draw(self):
        self.clear((0, 0, 0))
        self.ellipse(self.width // 2, self.height // 2, 200, 200)
        self.save_frame("save_frame_example_out.png")
        self.no_loop()


if __name__ == '__main__':
    SaveFrameExample().run()
