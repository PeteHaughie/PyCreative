"""
transforms_example.py: Example sketch demonstrating geometric transformations.
"""

from pycreative.app import Sketch

class TransformExample(Sketch):
    def setup(self):
        self.size(480, 320)
        self.bg = (240, 240, 240)
        self.set_title("Geometric Transformations Example")

    def update(self, dt):
        self.t = self.frame_count / 60.0  # time in seconds
        self.x = self.sin(self.t) * 100 + self.width / 2
        self.y = self.cos(self.t) * 100 + self.height / 2
        self.scale = (self.sin(self.t * 2) + 1) / 2
        self.angle = self.radians(self.t % 360) * 20

    def draw(self):
        self.clear(self.bg)

        # base rectangle
        self.fill((200, 50, 50))
        self.stroke((0, 0, 0))
        self.stroke_weight(2)

        with self.surface.transform(translate=(40, self.y - 40)):
            self.rect(40, 40, 80, 60)

        # translated rectangle
        with self.surface.transform(translate=(160, 30), scale=(0.5 + self.scale, 0.5 + self.scale / 3), rotate=0):
            self.fill((50, 200, 50))
            self.rect(40, 40, 80, 60)

        # rotated group
        with self.surface.transform(translate=(300, 140), rotate=self.angle):
            self.fill((50, 100, 220))
            self.rect(-40, -30, 80, 60)
            self.fill((240, 200, 50))
            self.ellipse(0, 0, 30, 30)

        # scaled group
        with self.surface.transform(translate=(self.x, self.y), rotate=-self.angle / 2):
            self.fill((180, 80, 180))
            self.rect(0, 0, 40, 30)
            self.stroke((0, 0, 0))
            self.line(-10, -20, 80, 40, stroke=(0, 0, 0), stroke_width=3)


if __name__ == '__main__':
    TransformExample().run()
