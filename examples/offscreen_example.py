"""
offscreen_example.py: Example sketch demonstrating offscreen surface caching.
"""

from pycreative.app import Sketch


class OffscreenExample(Sketch):
    """Offscreen Surface caching demo.

    Renders expensive static content into an offscreen buffer once in
    `setup()` and blits it during `draw()`. This file is runnable both via
    `python examples/offscreen_example.py` and the `pycreative` CLI.
    """

    def setup(self):
        self.size(800, 600)
        self.set_title("Offscreen Surface Caching Example")
        self.bg = (240, 240, 240)
        # Enable runtime no-loop mode: draw() will run once then pause.
        self.no_loop()

        # Create an offscreen surface and render the expensive static content once.
        self.off = self.create_graphics(800, 600, inherit_state=True)
        self.img = self.load_image("flowers.jpg")
        if not self.img:
            print("Failed to load image. Make sure 'data/flowers.jpg' is in the same directory.")
            self.img = None

        # Render expensive static content into the offscreen buffer in setup().
        with self.off:
            # clear using an RGB tuple (type-checkers expect 3-tuple)
            self.off.clear((0, 0, 0))
            self.off.no_fill()
            self.off.no_stroke()

            for i in range(10):
                self.off.line(
                    50,
                    50 + i * 10,
                    self.width / 2,
                    50 + i * 10,
                    stroke=(255, 255, 255),
                    stroke_width=1,
                )
            self.off.rect(
                50,
                self.height / 2 - 100,
                self.width / 2 - 50,
                100,
                fill=(255, 100, 100),
                stroke=(0, 0, 0),
                stroke_width=2,
            )
            self.off.ellipse(
                225,
                self.height - 150,
                200,
                200,
                fill=(100, 255, 100),
                stroke=(0, 0, 0),
                stroke_width=2,
            )
            # right hand side of canvas
            self.off.triangle(
                self.width / 2 + 50,
                50,
                self.width - 50,
                50,
                self.width - 200,
                150,
                stroke=(255, 255, 0),
                stroke_width=3,
                fill=(0, 0, 255),
            )
            self.off.quad(
                self.width / 2 + 50,
                self.height / 2 - 100,
                self.width - 50,
                self.height / 2 - 100,
                self.width - 100,
                self.height / 2,
                self.width / 2 + 100,
                self.height / 2,
                stroke=(0, 255, 255),
                stroke_width=3,
                fill=(255, 0, 0),
            )
            self.off.arc(
                self.width / 2 + 100,
                self.height / 2 + 100,
                100,
                100,
                self.radians(30),
                self.radians(300),
                mode="open",
                fill=(255, 100, 100),
                stroke=(100, 255, 100),
                stroke_width=2,
            )
            self.off.arc(
                self.width / 2 + 200,
                self.height / 2 + 100,
                100,
                100,
                self.radians(30),
                self.radians(300),
                mode="pie",
                fill=(100, 100, 255),
                stroke=(255, 100, 100),
                stroke_width=2,
            )
            self.off.arc(
                self.width / 2 + 300,
                self.height / 2 + 100,
                100,
                100,
                self.radians(30),
                self.radians(300),
                mode="chord",
                fill=(100, 255, 100),
                stroke=(100, 100, 255),
                stroke_width=2,
            )
            if self.img:
                # Draw the image at the center of the window
                img_w, img_h = self.img.get_size()
                print(f"Loaded image size: {img_w}x{img_h}")
                self.off.image(self.img, 100, 150, img_w / 5, img_h / 5)

    def draw(self):
        # Keep draw() simple and idiomatic: compose pre-rendered graphics.
        self.clear(self.bg)

        # query the offscreen pixel size from the OffscreenSurface public API
        w, h = 800, 600

        # blit the pre-rendered offscreen onto the main canvas
        self.image(self.off, 10, 10, w - 20, h - 20)
        print("Offscreen surface drawn")
        self.no_loop()


if __name__ == "__main__":
    OffscreenExample().run()
