"""
image_example.py: Example sketch demonstrating image loading and rendering using PyCreative.
"""

from pycreative import Sketch


class ImageExample(Sketch):
    def setup(self):
        self.size(640, 480)
        # Load an image (ensure 'data/dont.png' is in the same directory)
        self.img = self.load_image("dont.png")
        if not self.img:
            print(
                "Failed to load image. Make sure 'data/dont.png' is in the same directory."
            )
            self.img = None

    def draw(self):
        self.clear((0, 0, 0))
        if self.img:
            # Draw the image at the center of the window
            img_w, img_h = self.img.get_size()
            self.image(
                self.img, 100, 150, img_w / 10, img_h / 10
            )  # Draw at (100, 150) at 10% size


if __name__ == "__main__":
    ImageExample().run()
