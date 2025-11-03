class Sketch:
    def setup(self):
        # Window and layout
        self.size(800, 480)
        self.window_title('PCImage demo')

        # Attempt to load an example image from data/; if missing, create one
        self.photo = self.load_image('dont.png')
        if not self.photo:
            # create a checkerboard test image
            self.photo = self.create_image(200, 200)
            for y in range(200):
                for x in range(200):
                    if ((x // 20) + (y // 20)) % 2 == 0:
                        self.photo.set(x, y, (255, 200, 0, 255))
                    else:
                        self.photo.set(x, y, (200, 100, 255, 255))

        # Demonstrate copy() and in-place resize
        self.copy_img = self.photo.copy()
        self.copy_img.resize(100, 100)  # mutates copy_img in-place

        # Demonstrate proportional resize (returns a new image when one dim is 0)
        self.proportional = self.photo.resize(0, 120)  # returns a NEW PCImage, original unchanged

        # Demonstrate mask(): create an alpha mask with a circular opaque centre
        mask = self.create_image(self.photo.width, self.photo.height)
        # default pixels are transparent; draw an opaque circle in mask
        cx = self.photo.width // 2
        cy = self.photo.height // 2
        r = min(cx, cy) // 1
        for y in range(self.photo.height):
            for x in range(self.photo.width):
                dx = x - cx
                dy = y - cy
                if dx*dx + dy*dy <= (min(cx,cy)//2)**2:
                    mask.set(x, y, (0, 0, 0, 255))
                else:
                    mask.set(x, y, (0, 0, 0, 0))
        self.masked = self.photo.copy()
        self.masked.mask(mask)

        # Demonstrate filter
        self.gray = self.photo.filter('GRAY')
        self.thresh = self.photo.filter('THRESHOLD')

        # Demonstrate blend: create a small overlay and blend into a copy
        overlay = self.create_image(60, 60)
        for y in range(60):
            for x in range(60):
                overlay.set(x, y, (255, 0, 0, 200))
        self.blended = self.photo.copy()
        # blend overlay at (20,20)
        self.blended.blend(overlay, mode='ADD', dx=20, dy=20)

        # Save a snapshot key available later
        self.saved = False
        # Apply a global tint to demonstrate tint() -> affects subsequent image() draws
        try:
            self.tint((0, 180, 0, 180))
        except Exception:
            pass

    def draw(self):
        # Layout: original, copy, proportional
        self.image(self.photo, 10, 10)
        self.image(self.copy_img, 230, 10)
        self.image(self.proportional, 350, 10)

        # Masked and filters
        self.image(self.masked, 10, 230)
        if self.gray:
            self.image(self.gray, 230, 230)
        if self.thresh:
            self.image(self.thresh, 350, 230)

        # Blended
        self.image(self.blended, 470, 10)

        # Simple labels drawn via the engine's text fallback if available
        try:
            # Some environments may not provide text; avoid failing
            self.fill(0)
            self.text = getattr(self, 'text', None)
            if callable(self.text):
                self.text('original', 10, 220)
                self.text('copy (100x100)', 230, 220)
                self.text('proportional (h=120)', 350, 220)
                self.text('masked', 10, 430)
                self.text('gray', 230, 430)
                self.text('thresh', 350, 430)
                self.text('blended', 470, 220)
        except Exception:
            pass

    def key_pressed(self):
        # press 's' to save a snapshot of the canvas
        if self.key == 's' and not self.saved:
            self.save_frame('pcimage_demo-####.png')
            self.saved = True
