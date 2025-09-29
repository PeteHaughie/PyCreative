"""
graphics_demo.py: Example sketch using pycreative.graphics.Surface primitives in Sketch format.
"""

from pycreative.app import Sketch


class GraphicsDemo(Sketch):
    def setup(self):
        """
        It is possible to switch between the CairoSurface and Pygame Surface backends by changing the mode parameter in self.size().
        For CairoSurface, use mode='cairo'. For Pygame Surface, omit the mode parameter.
        """
        self.size(800, 600)
        self.bg = 100 # it also accepts an RGB tuple for color
        # self.bg = (10, 10, 10)
        self.set_title("Graphics Example")
        self.img = self.load_image("dont.png")
        if not self.img:
            print(
                "Failed to load image. Make sure 'data/dont.png' is in the same directory."
            )
            self.img = None
        """
        Global strokes and fills can be controlled using the following methods:
        self.stroke(r, g, b)  # Set stroke color
        self.stroke(r, g, b, a)  # Set stroke color with alpha
        self.stroke_width(px)  # Set stroke width
        self.noStroke()  # Disable stroke
        self.fill(r, g, b)  # Set fill color
        self.fill(r, g, b, a)  # Set fill color with alpha
        self.noFill()  # Disable fill
        """

    def draw(self):
        self.clear(self.bg)
        # left hand side of canvas
        for i in range(10):
            self.line(
                50,
                50 + i * 10,
                self.width / 2,
                50 + i * 10,
                stroke=(255, 255, 255),
                stroke_width=1,
            )
        self.rect(50, self.height / 2 - 100, self.width / 2 - 50, 100)
        self.ellipse(225, self.height - 150, 200, 200)
        # right hand side of canvas
        self.triangle(
            self.width / 2 + 50, 50, self.width - 50, 50, self.width - 200, 150
        )
        self.quad(
            self.width / 2 + 50,
            self.height / 2 - 100,
            self.width - 50,
            self.height / 2 - 100,
            self.width - 100,
            self.height / 2,
            self.width / 2 + 100,
            self.height / 2,
        )
        self.arc(
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
        self.arc(
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
        self.arc(
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
            self.image(
                self.img, 100, 150, img_w / 10, img_h / 10
            )  # Draw at (100, 150) at 10% size


if __name__ == "__main__":
    GraphicsDemo().run()
