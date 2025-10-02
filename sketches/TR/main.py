"""
PImage img;
PGraphics pg;
int elements = 64;
int dur = 100;

void setup() {
  size(288, 512);
  pg = createGraphics(72, 128);
}

void draw() {
  drawPg();
  image(pg, 0, 0, width, height);
}
"""

from pycreative.app import Sketch
from pg import draw_pg

class MySketch(Sketch):
    def setup(self):
        self.size(288, 512)
        self.set_title("Tim Rodenbroeker")
        self.set_double_buffer(True)   # default True
        self.set_vsync(1)              # enable vsync
        self.frame_rate(60)            # keep frame rate capped
        self.pg = self.create_graphics(72, 128)
        print("Hi Tim!")

    def draw(self):
        draw_pg(self)
        self.image(self.pg, 0, 0, self.width, self.height)

if __name__ == "__main__":
    MySketch().run()