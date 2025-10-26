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

from Emitter import Emitter


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example_4_08 Image_Texture_System_Smoke")
        self.img = self.load_image("texture.png")
        self.emitter = Emitter(self, int(self.width / 2), self.height - 75)
        self.frame_rate(30)

    def draw(self):
        self.background(0)
        dx = self.map(self.mouse_x, 0, self.width, -0.2, 0.2)
        wind = self.pcvector(dx, 0)
        self.emitter.apply_force(wind)
        self.emitter.run()
        self.emitter.add_particle()
        self.draw_vector(wind, self.pcvector(self.width / 2, 50), 500)

    def draw_vector(self, v, pos, scayl):
        self.push_matrix()
        arrowsize = 4
        self.translate(pos.x, pos.y)
        self.stroke(255)
        self.rotate(v.heading())
        length = v.mag() * scayl
        self.line(0, 0, length, 0)
        self.line(length, 0, length - arrowsize, +arrowsize / 2)
        self.line(length, 0, length - arrowsize, -arrowsize / 2)
        self.pop_matrix()
