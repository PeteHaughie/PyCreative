from pycreative.app import Sketch


class ShapeExample(Sketch):
    def setup(self):
        self.size(400, 300)
        self.set_title("Shape Construction Example")
        self.bg = (30, 30, 30)

        # Pre-render a custom polygon into an offscreen buffer
        self.off = self.create_graphics(200, 150)
        with self.off:
            self.off.clear((0, 0, 0))
            self.off.fill((200, 100, 50))
            # draw a custom star-like polygon using begin/vertex/end
            self.off.begin_shape()
            self.off.vertex(100, 10)
            self.off.vertex(120, 60)
            self.off.vertex(180, 60)
            self.off.vertex(130, 95)
            self.off.vertex(150, 140)
            self.off.vertex(100, 110)
            self.off.vertex(50, 140)
            self.off.vertex(70, 95)
            self.off.vertex(20, 60)
            self.off.vertex(80, 60)
            self.off.end_shape(close=True)

    def draw(self):
        self.clear(self.bg)
        # center the offscreen image
        w, h = self.off.size
        x = (self.width - w) // 2
        y = (self.height - h) // 2
        self.image(self.off, x, y)


if __name__ == "__main__":
    ShapeExample().run()
