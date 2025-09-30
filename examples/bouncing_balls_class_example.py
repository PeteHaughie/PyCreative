from pycreative.app import Sketch
import random
import ball_class

class BouncingBallsClassExample(Sketch):
    def setup(self):
        self.size(600, 400)
        self.set_title("Bouncing Balls Class Example")
        self.frame_rate(60)
        self.bg = (0, 0, 0)
        self.no_stroke()

        # Create multiple balls with random velocities
        self.balls = [
            ball_class.Ball(
                self.width // 2,
                self.height // 2,
                15,
                (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                [random.uniform(-10, 10), random.uniform(-10, 10)],
            )
            for i in range(100)
        ]

    def update(self, dt):
        for ball in self.balls:
            ball.update(self.width, self.height)

    def draw(self):
        self.clear(self.bg)
        for ball in self.balls:
            ball.draw(self)
