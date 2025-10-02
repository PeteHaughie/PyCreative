"""Example demonstrating mouse press/release usage.

Run with:
    python examples/mouse_pressed_example.py

This example shows two styles:
 - Implementing `on_event(self, event)` and handling mouse events manually.
 - Implementing the Processing-style `mouse_pressed()` / `mouse_released()` hooks
   — the input dispatcher will call these for convenience.
"""
from pycreative.app import Sketch


class MousePressedExample(Sketch):
    def setup(self):
        self.size(320, 160)
        self.pressed_count = 0

    def update(self, dt):
        pass

    def draw(self):
        # just print a simple status line
        print(f"pressed_count={self.pressed_count}", end='\r')

    def on_event(self, event):
        # Demonstrate the normalized Event object
        if event.type == "mouse":
            print(f"on_event: mouse at={event.pos} button={event.button}")

    def mouse_pressed(self):
        # processing-style hook — will be called by the dispatcher
        self.pressed_count += 1
        print(f"mouse_pressed() called -> {self.pressed_count}")

    def mouse_released(self):
        print("mouse_released() called")


if __name__ == '__main__':
    MousePressedExample(sketch_path=__file__).run()
