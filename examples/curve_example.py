from pycreative.app import Sketch
import pygame


class CurveExample(Sketch):
    def setup(self):
        self.size(480, 200)
        self.bg = (240, 240, 240)

    def draw(self):
        self.clear(self.bg)
        self.stroke((0, 0, 0))
        self.stroke_weight(2)

        # Draw multiple curves with differing tightness
        y = 40
        points = [(10, y + 40), (80, y), (180, y + 40), (260, y)]
        tightness_vals = [0.0, 0.3, 0.6, 0.9]
        for i, t in enumerate(tightness_vals):
            self.no_fill()
            self.stroke((int(60 + i * 40), 20, 180))
            self.stroke_weight(3)
            # set tightness on the drawing surface
            self.surface.curve_tightness(t)
            x0, y0 = points[0]
            x1, y1 = points[1]
            x2, y2 = points[2]
            x3, y3 = points[3]
            # offset vertically per row
            offset = i * 30
            # draw via the surface API
            self.surface.curve(x0, y0 + offset, x1, y1 + offset, x2, y2 + offset, x3, y3 + offset)

        # Save a snapshot for visual inspection then stop
        # try:
        #     pygame.image.save(self.surface.raw, "curve_example_out.png")
        #     print("Saved curve_example_out.png")
        # except Exception:
        #     pass
        self.no_loop()


if __name__ == "__main__":
    CurveExample().run()
