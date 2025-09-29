from pycreative.app import Sketch


class StyleOverrideDemo(Sketch):
    def setup(self):
        self.size(200, 120)
        # global drawing state
        self.fill((240, 240, 240))
        self.stroke((0, 0, 0))
        self.stroke_weight(2)

    def draw(self):
        self.clear((255, 255, 255))

        # Uses global stroke (black)
        self.line(10, 20, 190, 20)

        # Per-call override: filled rectangle with blue fill
        self.rect(10, 30, 60, 40, fill=(0, 128, 255))

        # Per-call override: outlined ellipse with red stroke and thicker weight
        self.ellipse(120, 50, 60, 40, fill=None, stroke=(255, 0, 0), stroke_weight=4)

        # Per-call override on polyline
        pts = [(10, 90), (60, 110), (110, 80), (160, 100)]
        self.polyline(pts, stroke=(0, 150, 0), stroke_width=3)


if __name__ == "__main__":
    StyleOverrideDemo().run()
