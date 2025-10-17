import ball_class


class Sketch:
  def setup(self):
    self.size(600, 400)
    self.window_title("Bouncing Balls Class Example")
    self.frame_rate(60)
    self.bg = 255
    self.no_stroke()
    # Create multiple balls with random velocities
    self.balls = [
      ball_class.Ball(
        self.width // 2,
        self.height // 2,
        15,
        (self.round(self.random(0, 255)), self.round(self.random(0, 255)), self.round(self.random(0, 255))),
        [self.round(self.uniform(-50, 50)), self.round(self.uniform(-50, 50))],
      )
      for i in range(100)
    ]

  def update(self, dt):
    for ball in self.balls:
      ball.update(self.width, self.height)

  def draw(self):
    self.background(self.bg)
    for ball in self.balls:
      ball.draw(self)
