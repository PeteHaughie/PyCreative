from pycreative.app import Sketch


class PixelsExample(Sketch):
    def setup(self):
        self.size(640, 480)
        self.set_title("Pixels Example")

    def draw(self):
        self.clear((32, 64, 96))
        # Generate a simple gradient using the pixel API. If numpy/surfarray
        # is available `get_pixels()` returns a numpy array which we can
        # manipulate efficiently; otherwise fallback to per-pixel writes.
        arr = self.surface.get_pixels()
        try:
            # Try array-like bulk write without importing numpy in the sketch.
            # Works with numpy arrays and list-of-lists (slower).
            h, w, c = arr.shape
            for y in range(h):
                gy = int(y * 255 / max(1, h - 1))
                for x in range(w):
                    gx = int(x * 255 / max(1, w - 1))
                    arr[y, x, 0] = gx
                    arr[y, x, 1] = gy
                    arr[y, x, 2] = 80
            self.surface.set_pixels(arr)
        except Exception:
            # Fallback: per-pixel writes
            w, h = self.surface.size
            for y in range(h):
                for x in range(w):
                    r = int(x * 255 / max(1, w - 1))
                    g = int(y * 255 / max(1, h - 1))
                    b = 80
                    self.surface.set_pixel(x, y, (r, g, b))

        self.save_snapshot("pixels_example_out.png")
        self.no_loop()


if __name__ == '__main__':
    PixelsExample().run()
