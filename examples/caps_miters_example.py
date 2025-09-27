from pycreative import Sketch

class CairoCapsMitersSketch(Sketch):
    def setup(self):
        self.size(600, 400)
        self.set_title("Cairo Stroke Caps & Miters Example")
        self.bg = (255)
        self.stroke_weight(16)
        self._caps = ["butt", "round", "square"]
        self._joins = ["miter", "round", "bevel"]

    def draw(self):
        self.clear(self.bg)
        y = 60
        x0, x1 = 80, 520
        # Draw lines with different caps
        for i, cap in enumerate(self._caps):
            self.stroke_cap(cap)
            self.stroke((40, 80, 200))
            self.line(x0, y, x1, y)
            self.text(f"cap: {cap}", x0, y - 30, color=(40,40,40), size=18)
            y += 60
        # Draw polylines with different joins
        y = 260
        for i, join in enumerate(self._joins):
            self.stroke_join(join)
            self.stroke_cap(self._caps[i % len(self._caps)])
            self.stroke((200, 80, 40))
            self.polyline([(180, y), (300, y - 50), (420, y)], color=(40, 80, 200), width=18)
            self.text(f"join: {join}", x0, y, color=(40,40,40), size=18)
            y += 40

    def stroke_cap(self, cap):
        # Set Cairo line cap
        if hasattr(self._surface, "set_line_cap") and self._surface:
            self._surface.set_line_cap(cap)

    def stroke_join(self, join):
        # Set Cairo line join
        if hasattr(self._surface, "set_line_join") and self._surface:
            self._surface.set_line_join(join)

if __name__ == "__main__":
    CairoCapsMitersSketch().run()
