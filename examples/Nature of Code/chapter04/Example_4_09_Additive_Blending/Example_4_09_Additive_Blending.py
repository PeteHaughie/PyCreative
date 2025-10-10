"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter4/Example_4_9_Additive_Blending/Example_4_9_Additive_Blending.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Smoke Particle System

// A basic smoke effect using a particle system
// Each particle is rendered as an alpha masked image
"""

from pycreative.app import Sketch
from Emitter import Emitter


class Example_4_09_Additive_Blending(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example_4_09_Additive_Blending")
        self.img = self.load_image("texture.png")
        self.emitter = Emitter(self, int(self.width / 2), self.height - 75, self.img)
        self.frame_rate(30)

    def draw(self):
        self.background(0)
        # Additive blending!
        self.blend_mode('ADD')

        # Calculate a "wind" force based on mouse horizontal position
        dx = self.map(self.mouse_x or 0, 0, self.width, -0.2, 0.2)
        wind = self.pvector(dx, 0)
        self.emitter.apply_force(wind)
        self.emitter.run()
        for _ in range(3):
            self.emitter.add_particle()

        # Draw an arrow representing the wind force
        self.draw_vector(wind, self.pvector(self.width / 2, 50), 500)

    def draw_vector(self, v, pos, scayl):
        self.push()
        try:
          arrowsize = 4
          # Translate to position to render vector
          self.translate(pos.x, pos.y)
          self.stroke((255, 255, 255))
          # Call vector heading function to get direction (note that pointing up is a heading of 0) and rotate
          self.rotate(v.heading())
          # Calculate length of vector & scale it to be bigger or smaller if necessary
          length = v.mag() * scayl
          # Draw three lines to make an arrow (draw pointing up since we've rotate to the proper direction)
          self.line(0, 0, length, 0)
          self.line(length, 0, length - arrowsize, +arrowsize / 2)
          self.line(length, 0, length - arrowsize, -arrowsize / 2)
        finally:
          self.pop()
