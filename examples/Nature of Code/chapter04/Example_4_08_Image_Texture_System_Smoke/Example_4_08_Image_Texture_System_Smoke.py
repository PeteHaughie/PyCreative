"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter4/Example_4_8_Image_Texture_System_Smoke/Example_4_8_Image_Texture_System_Smoke.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Smoke Particle System

// A basic smoke effect using a particle system
// Each particle is rendered as an alpha masked image
"""

from pycreative.app import Sketch
from Emitter import Emitter


class Example_4_08_Image_Texture_System_Smoke(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example_4_08_Image_Texture_System_Smoke")
        self.img = self.load_image("texture.png")
        self.emitter = Emitter(self, int(self.width / 2), self.height - 75)
        self.frame_rate(30)

    def draw(self):
        self.background(0)
        dx = self.map(self.mouse_x or 0, 0, self.width, -0.2, 0.2)
        wind = self.pvector(dx, 0)
        self.emitter.apply_force(wind)
        self.emitter.run()
        self.emitter.add_particle()
        self.draw_vector(wind, self.pvector(self.width / 2, 50), 500)

    def draw_vector(self, v, pos, scayl):
        self.push()
        try:
          arrowsize = 4
          self.translate(pos.x, pos.y)
          self.stroke(255)
          self.rotate(v.heading())
          length = v.mag() * scayl
          self.line(0, 0, length, 0)
          self.line(length, 0, length - arrowsize, +arrowsize / 2)
          self.line(length, 0, length - arrowsize, -arrowsize / 2)
        finally:
          self.pop()