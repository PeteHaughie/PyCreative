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

        # Create an offscreen surface that we will re-render every frame.
        # Per-frame offscreen rendering is an idiomatic pattern: draw
        # into an offscreen buffer each frame and then blit it to the
        # main surface. This keeps the drawing code localized and lets
        # the offscreen surface manage its own transforms/state.
        self.off = self.create_graphics(800, 600, inherit_state=True)
        self.img = self.load_image("flowers.jpg")
        if not self.img:
            print("Failed to load image. Make sure 'data/flowers.jpg' is in the same directory.")
            self.img = None

    def update(self, dt):
        self.t = self.frame_count / 60.0  # time in seconds
        self.x = self.sin(self.t) * 100 + self.width / 2
        self.y = self.cos(self.t) * 100 + self.height / 2
        self.scale = (self.sin(self.t * 2) + 1) / 2
        self.angle = self.radians(self.t % 360) * 20


    def draw(self):
        # Keep draw() simple and idiomatic: compose pre-rendered graphics.
        self.clear(self.bg)

        # Render the offscreen surface each frame. We draw into `self.off`
        # so that all transforms and style state applied on that surface
        # affect the offscreen buffer consistently.
        with self.off:
            # clear the offscreen to a dark background so it contrasts
            # with the main canvas (you can choose any color here)
            self.off.clear((0, 0, 0))

            # background stripes
            self.off.no_fill()
            self.off.stroke((255, 255, 255))
            off_w, off_h = self.off.size
            for i in range(10):
                self.off.line(50, 50 + i * 10, off_w / 2, 50 + i * 10, stroke_width=1)

            # a rectangle that pulsates with `self.scale`
            rect_w = (off_w / 2 - 50) * (0.5 + self.scale * 0.5)
            self.off.fill((255, 100, 100))
            self.off.stroke((0, 0, 0))
            self.off.rect(50, off_h / 2 - 100, rect_w, 100, stroke_width=2)

            # moving ellipse
            ex = 225 + self.sin(self.t * 1.5) * 40
            ey = off_h - 150 + self.cos(self.t * 1.2) * 20
            self.off.fill((100, 255, 100))
            self.off.ellipse(ex, ey, 200 * (0.8 + self.scale * 0.4), 200 * (0.8 + self.scale * 0.4), stroke_width=2)

            # right-hand shapes
            self.off.fill((255, 0, 0))
            self.off.stroke((0, 255, 255))
            self.off.quad(off_w / 2 + 50, off_h / 2 - 100, off_w - 50, off_h / 2 - 100, off_w - 100, off_h / 2, off_w / 2 + 100, off_h / 2, stroke_width=3)

            # arcs
            self.off.arc(off_w / 2 + 100, off_h / 2 + 100, 100, 100, self.radians(30), self.radians(300), mode="pie", fill=(100, 100, 255), stroke_width=2)

            # optional image (scaled)
            if self.img:
                img_w, img_h = self.img.get_size()
                self.off.image(self.img, 100, 150, img_w / 5, img_h / 5)

            # draw a rotating triangle inside the offscreen buffer using the
            # offscreen's transform context so rotation happens about the
            # offscreen origin
            with self.off.transform(translate=(off_w / 2, 80), rotate=self.angle, scale=(1 + self.scale * 0.5, 1 + self.scale * 0.5)):
                self.off.fill((0, 0, 255))
                self.off.stroke((255, 255, 0))
                self.off.triangle(-50, -20, 150, -20, 50, 80, stroke_width=3)

        # blit the offscreen surface onto the main canvas, centered with a margin
        w, h = 800, 600
        self.image(self.off, 10, 10, w - 20, h - 20)
