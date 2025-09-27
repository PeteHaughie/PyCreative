from pycreative import Sketch
from pycreative.graphicssurface import GraphicsSurface

class OffscreenSurfaceSketch(Sketch):
    def setup(self):
        self.size(800, 600)
        self.bg = (20, 20, 20)
        self.set_title("GraphicsSurface Offscreen Example")
        # Create an offscreen surface
        self.gfx = GraphicsSurface(self.width, self.height)
        self.gfx.clear((30, 30, 60))
        self.gfx.ellipse(200, 150, 180, 120, color=(255, 200, 40), width=0)
        self.gfx.line(0, 0, 400, 300, color=(200, 40, 40), width=8)
        self.gfx.rect(50, 50, 300, 200, color=(40, 200, 120), width=4)

    def draw(self):
        self.clear(self.bg)
        # Blit the offscreen surface to the main sketch
        self.image(self.gfx.surface, 200, 150, 400, 300)
        self.text("This is an offscreen GraphicsSurface", 400, 100, center=True, color=(255,255,255), size=28)

if __name__ == "__main__":
    OffscreenSurfaceSketch().run()
