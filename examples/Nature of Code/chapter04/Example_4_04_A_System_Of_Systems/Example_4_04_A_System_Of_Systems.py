"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter4/Example_4_4_A_System_Of_Systems/Example_4_4_A_System_Of_Systems.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 4-4: A System of Systems
"""

from Emitter import Emitter


class Sketch:
    def setup(self):
        self.size(640, 360)
        self.window_title("NOC: Example_4_04 A_System_Of_Systems")
        self.emitters = []

    def update(self, dt):
        for emitter in self.emitters:
            emitter.update()

    def draw(self):
        self.background(255)
        for emitter in self.emitters:
            emitter.draw()
            emitter.add_particle()

    def mouse_pressed(self):
        if self.mouse_x is not None and self.mouse_y is not None:  # Optional safety check and suppress type warning
            self.emitters.append(Emitter(self, self.mouse_x, self.mouse_y))
