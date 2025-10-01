"""Small example demonstrating calling rect_mode() in setup() before the display exists.

Run with:
    python examples/rect_mode_example.py

Press Escape to close the window (default behavior).
"""

from pycreative.app import Sketch


class RectModeExample(Sketch):
    def setup(self) -> None:
        # Request a window size before the display is created
        self.size(640, 480)
        self.set_title("Rect / Ellipse Mode Demo")

        # Call rect_mode and ellipse_mode in setup() — these will be recorded
        # as "pending" and applied once the display is created inside run().
        # This demonstrates the idiomatic API where setup() can configure
        # drawing state early.
        self.rect_mode("CENTER")
        self.ellipse_mode("CENTER")

        # Some simple style defaults
        self.fill((120, 200, 255))
        self.stroke((10, 10, 30))
        self.stroke_weight(4)

    def update(self, dt: float) -> None:
        # no-op
        return None

    def draw(self) -> None:
        # Clear to a soft background
        self.clear((30, 30, 40))

        cx = self.width // 2
        cy = self.height // 2

        # Draw a centered rectangle and a centered ellipse to show modes
        self.rect(cx, cy, 300, 180)
        # draw a slightly smaller ellipse on top
        self.ellipse(cx, cy, 220, 140)


if __name__ == "__main__":
    RectModeExample().run()
