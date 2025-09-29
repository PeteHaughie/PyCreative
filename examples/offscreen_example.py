# (file cleaned of Markdown fences)
# (file cleaned of Markdown fences)
from pycreative.app import Sketch

class OffscreenExample(Sketch):
    from pycreative.app import Sketch


    class OffscreenExample(Sketch):
        def setup(self):
            self.size(640, 360)
            self.set_title("Offscreen Surface Caching Example")
            self.bg = (240, 240, 240)
            # Enable runtime no-loop mode: draw() will run once then pause.
            self.no_loop()

            # Create an offscreen surface and render the expensive static content once.
            self.off = self.create_graphics(300, 200, inherit_state=True)

            # Render expensive static content into the offscreen buffer in setup().
            with self.off:
                # clear using an RGB tuple (type-checkers expect 3-tuple)
                self.off.clear((0, 0, 0))
                self.off.fill((30, 120, 200))
                self.off.stroke((255, 255, 255))
                self.off.stroke_weight(2)
                # many circles to simulate expensive work (rendered once)
                for i in range(0, 200, 10):
                    x = 100 + (i % 50) * 2
                    y = 100 + (i // 50) * 10
                    self.off.ellipse(x, y, 40, 40)

        def draw(self):
            # Keep draw() simple and idiomatic: compose pre-rendered graphics.
            self.clear(self.bg)

            # query the offscreen pixel size from the OffscreenSurface public API
            w, h = self.off.size
            x = (self.width - w) // 2
            y = (self.height - h) // 2

            # blit the pre-rendered offscreen onto the main canvas
            self.image(self.off, x, y)
            print("Offscreen surface drawn")


    if __name__ == "__main__":
        OffscreenExample().run()
