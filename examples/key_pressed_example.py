"""Example demonstrating key_pressed() usage.

Run with:
    python examples/key_pressed_example.py
"""
from pycreative.app import Sketch


class KeyPressedExample(Sketch):
    def setup(self):
        self.size(400, 200)
        self.count = 0

    def update(self, dt):
        pass

    def draw(self):
        # keep it simple: print the counter to the console
        print(f"space pressed: {self.count}", end='\r')

    def key_pressed(self):
        # `self.key` holds the readable name (e.g., 'space', 'a')
        if self.key == 'space':
            self.count += 1
            print(f"space pressed -> {self.count}")


if __name__ == '__main__':
    # Allow running directly
    KeyPressedExample(sketch_path=__file__).run()
