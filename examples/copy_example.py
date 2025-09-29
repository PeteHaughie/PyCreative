from pycreative.app import Sketch


class CopyExample(Sketch):

    def setup(self):
        self.size(640, 360)
        self.set_title("Copy Example")
        self.no_fill()
        self.no_stroke()
        # self.stroke((255, 255, 255))
        # self.stroke_weight(1)

    def draw(self):
        self.clear((0, 0, 0))

        # Load an image from file and draw it full-canvas
        flowers = self.load_image('flowers.jpg')
        if flowers is None:
            self.no_loop()
            return
        # draw the source image stretched to the canvas
        self.image(flowers, 0, 0, self.width, self.height)

        # Example A: copy from the loaded image object into the canvas
        # Prefer calling the image-like object's API so it's clear this
        # is an image-to-canvas operation.
        # Use: img.copy_to(dest_surface, sx, sy, sw, sh, dx, dy, dw, dh)
        # flowers.copy_to(self.surface, 56, 176, 80, 80, 280, 200, 80, 80)

        # Example B: copy a region of the canvas to another location
        # Use the main surface copy method for canvas-local copies.
        # Signature: self.copy(sx, sy, sw, sh, dx, dy, dw, dh)
        self.copy(350, 130, 80, 80, 10, 20, 160, 160)

        # Draw a rectangle showing the area that was copied from the source
        self.rect(350, 130, 80, 80, stroke=(255, 255, 255), stroke_width=1)

        # Example C: small pixel-manipulation using the context manager
        # Darken the copied-up region by operating on pixels directly.
        # with self.surface.pixels() as pv:
        #     h, w, c = pv.shape
        #     for yy in range(20, 180):
        #         for xx in range(360, 520):
        #             # clamp to surface bounds
        #             if 0 <= yy < h and 0 <= xx < w:
        #                 px = pv[yy, xx]
        #                 # px may be a numpy array, tuple, or list; read channels
        #                 r = int(px[0]); g = int(px[1]); b = int(px[2])
        #                 if len(px) >= 4:
        #                     a = int(px[3])
        #                     pv[yy, xx] = (max(0, r - 50), g, b, a)
        #                 else:
        #                     pv[yy, xx] = (max(0, r - 50), g, b)

        self.no_loop()


if __name__ == '__main__':
    CopyExample().run()
