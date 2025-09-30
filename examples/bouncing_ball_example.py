from pycreative.app import Sketch

class BouncingBallExample(Sketch):
    def setup(self):
        self.size(400, 300)
        self.set_title("Bouncing Ball Example")
        self.frame_rate(60)
        self.bg = (0, 0, 0)
        self.no_stroke()

        # Ball properties
        self.ball_pos = [200, 150]
        self.ball_vel = [3, 2]
        self.ball_radius = 15

        # Set drawing styles
        self.fill((255, 0, 0))
        self.stroke((0, 0, 0))
        self.stroke_weight(2)

    def update(self, dt):
        # Update ball position
        self.ball_pos[0] += self.ball_vel[0]
        self.ball_pos[1] += self.ball_vel[1]

        # Bounce off walls
        if self.ball_pos[0] <= self.ball_radius or self.ball_pos[0] >= self.width - self.ball_radius:
            self.ball_vel[0] *= -1
        if self.ball_pos[1] <= self.ball_radius or self.ball_pos[1] >= self.height - self.ball_radius:
            self.ball_vel[1] *= -1

    def draw(self):
        self.clear(self.bg)
        # Draw the ball
        self.ellipse(self.ball_pos[0], self.ball_pos[1], self.ball_radius * 2, self.ball_radius * 2)

if __name__ == "__main__":
    BouncingBallExample().run()