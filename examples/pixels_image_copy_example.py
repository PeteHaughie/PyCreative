from pycreative.app import Sketch


class PixelsImageCopyExample(Sketch):

    def setup(self):
        self.size(640, 360)
        self.set_title("Pixels Image Copy Example")

    def draw(self):
        self.clear((0, 0, 0))

        # Load an image from file
        flowers = self.load_image('flowers.jpg')
        if flowers is None:
            self.no_loop()
            return
        w = int(self.width / 2)
        # Draw the full image scaled to fill the canvas
        self.image(flowers, 0, 0, self.width, self.height)
        # Copy the right half of the image to the left half of the canvas
        self.copy(flowers, w, 0, w, int(self.height), 0, 0, w, int(self.height))

        self.no_loop()


if __name__ == '__main__':
    PixelsImageCopyExample().run()
