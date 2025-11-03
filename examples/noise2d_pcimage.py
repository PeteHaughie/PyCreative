class Sketch:
    """Draw a 2D noise field into a PCImage pixel buffer and display it.

    This sketch demonstrates using `create_image`, per-pixel `set`, and
    `image()` to draw a procedurally generated noise texture. No external
    libraries are required.
    """

    def setup(self):
        self.size(800, 600)
        self.window_title('Noise2D -> PCImage demo')

        w, h = self.width, self.height
        # create an RGBA PCImage we will write into directly
        self.noise_img = self.create_image(w, h)

        # Use the built-in noise API provided by the engine. Configure
        # the noise detail (octaves/falloff) and optionally seed it for
        # reproducible output.
        octaves = 5
        falloff = 0.5
        self.noise_detail(octaves, falloff)
        self.noise_seed(int(self.random(0, 10000)))

        # Fill the PCImage by writing pixels using the built-in noise()
        scale = 0.008  # controls noise frequency
        for y in range(h):
            for x in range(w):
                n = float(self.noise(x * scale, y * scale))
                # map from [0,1] to grayscale
                v = int(max(0, min(255, round(n * 255))))
                # a simple color ramp: shift hue by x for visual interest
                r = (v + (x // 4)) % 256
                g = v
                b = (v + (y // 6)) % 256
                self.noise_img.set(x, y, (r, g, b, 255))

        # mark pixels ready/update if needed
        self.noise_img.update_pixels()

    def draw(self):
        # draw the generated noise texture to the canvas
        self.image(self.noise_img, 0, 0)

    def key_pressed(self):
        # press 's' to save a snapshot of the current canvas
        if getattr(self, 'key', None) == 's':
            self.save_frame('noise2d-####.png')
