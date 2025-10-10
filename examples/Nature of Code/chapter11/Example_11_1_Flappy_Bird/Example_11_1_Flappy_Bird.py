"""
This is a recreation of the Nature of Code example found at:
https://github.com/nature-of-code/noc-2-processing-port/blob/main/chapter11/Example_11_1_Flappy_Bird/Example_11_1_Flappy_Bird.pde

// The Nature of Code
// Daniel Shiffman
// http://natureofcode.com

// Example 11-1: Flappy Bird
"""

from pycreative.app import Sketch
from Bird import Bird
from Pipe import Pipe


class Example_11_1_Flappy_Bird(Sketch):
    def setup(self):
        self.size(640, 360)
        self.set_title("Example 11-1: Flappy Bird")
        self.bird = Bird(self)
        self.pipes = [Pipe(self)]

    def draw(self):
        self.background(255)

        for i in range(len(self.pipes) - 1, -1, -1):
            self.pipes[i].show()
            self.pipes[i].update()

            if self.pipes[i].collides(self.bird):
                self.text("OOPS!", self.pipes[i].x, int(self.pipes[i].top + 20))

            if self.pipes[i].offscreen():
                self.pipes.pop(i)

        self.bird.update()
        self.bird.show()

        if self.frame_count % 100 == 0:
            self.pipes.append(Pipe(self))

    def mouse_pressed(self):
        self.bird.flap()
