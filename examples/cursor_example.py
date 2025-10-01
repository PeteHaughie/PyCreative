from pycreative.app import Sketch


class CursorExample(Sketch):
    def setup(self):
        self.size(320, 240)
        self.set_title("Cursor Example")
        # Hide cursor during this sketch
        self.no_cursor()

    def draw(self):
        # draw nothing; this example shows cursor control
        print("Cursor position:", self.mouse_x, self.mouse_y)


if __name__ == "__main__":
    CursorExample().run()
